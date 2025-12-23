// =============================================================================
// x402 Payment Hook
// =============================================================================
// Handles EIP-3009 TransferWithAuthorization signing and submission.
// =============================================================================

import { useState } from 'react'
import { useAccount, useSignTypedData } from 'wagmi'
import { plasma } from './wagmi'

interface PaymentOptions {
  invoiceId: string
  paymentOptions: Array<{
    network: string
    chainId: number
    token: string
    amount: string
    recipient: string
    deadline: number
    nonce: string
  }>
}

export function usePayment() {
  const { address } = useAccount()
  const { signTypedDataAsync } = useSignTypedData()
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const processPayment = async (invoice: PaymentOptions) => {
    setIsProcessing(true)
    setError(null)

    try {
      const option = invoice.paymentOptions.find(
        (opt) => opt.chainId === plasma.id
      )

      if (!option) {
        throw new Error('No valid payment option for Plasma network')
      }

      if (!address) {
        throw new Error('Wallet not connected')
      }

      // EIP-3009 Typed Data
      const domain = {
        name: 'USD₮', // Ensure this matches contract name (USD₮ or USD₮0)
        version: '1',
        chainId: option.chainId,
        verifyingContract: option.token as `0x${string}`,
      }

      const types = {
        TransferWithAuthorization: [
          { name: 'from', type: 'address' },
          { name: 'to', type: 'address' },
          { name: 'value', type: 'uint256' },
          { name: 'validAfter', type: 'uint256' },
          { name: 'validBefore', type: 'uint256' },
          { name: 'nonce', type: 'bytes32' },
        ],
      }

      const value = {
        from: address,
        to: option.recipient as `0x${string}`,
        value: BigInt(option.amount),
        validAfter: BigInt(0),
        validBefore: BigInt(option.deadline),
        nonce: option.nonce as `0x${string}`,
      }

      // Sign the typed data
      const signature = await signTypedDataAsync({
        domain,
        types,
        primaryType: 'TransferWithAuthorization',
        message: value,
      })

      // Parse signature (r, s, v)
      // Wagmi returns hex string, we need to split it if backend expects components
      // However, backend likely expects r, s, v components.
      // We can use viem's parseSignature or do it manually.
      // For now let's send hex and let backend parse if needed, OR parse it here.
      // Our backend x402_service.py expects dict with v, r, s
      
      // Basic signature parsing
      const r = signature.slice(0, 66)
      const s = '0x' + signature.slice(66, 130)
      const v = parseInt(signature.slice(130, 132), 16)

      const payload = {
        invoiceId: invoice.invoiceId,
        scheme: 'eip3009-transfer-with-auth',
        signature: { v, r, s },
        chosenOption: option,
      }

      // Submit payment
      const response = await fetch('/api/v1/payment/pay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Payment submission failed')
      }

      const result = await response.json()
      return result

    } catch (err) {
      console.error(err)
      setError(err instanceof Error ? err.message : 'Payment failed')
      throw err
    } finally {
      setIsProcessing(false)
    }
  }

  const createInvoice = async (payerAddress: string) => {
    const response = await fetch('/api/v1/payment/invoice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payer_address: payerAddress }),
    })

    if (!response.ok) {
      throw new Error('Failed to create invoice')
    }

    return await response.json()
  }

  return {
    processPayment,
    createInvoice,
    isProcessing,
    error,
  }
}

