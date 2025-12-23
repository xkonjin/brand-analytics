// =============================================================================
// Payment Modal Component
// =============================================================================
// Displays payment prompt and handles wallet connection/signing.
// =============================================================================

'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount } from 'wagmi'
import { usePayment } from '@/lib/usePayment'
import { useState, useEffect } from 'react'
import { Loader2, CheckCircle2 } from 'lucide-react'

interface PaymentModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  invoiceData: any
  onSuccess: (invoiceId: string) => void
}

export function PaymentModal({ open, onOpenChange, invoiceData: initialInvoice, onSuccess }: PaymentModalProps) {
  const { isConnected, address } = useAccount()
  const { processPayment, createInvoice, isProcessing, error: hookError } = usePayment()
  const [success, setSuccess] = useState(false)
  const [invoice, setInvoice] = useState(initialInvoice)
  const [loadingInvoice, setLoadingInvoice] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)

  // Fetch invoice when wallet connects if not already provided
  useEffect(() => {
    if (open && isConnected && address && !invoice && !loadingInvoice) {
      setLoadingInvoice(true)
      createInvoice(address)
        .then(data => {
          setInvoice(data)
          setLocalError(null)
        })
        .catch(err => {
          setLocalError("Failed to generate invoice")
          console.error(err)
        })
        .finally(() => setLoadingInvoice(false))
    }
  }, [open, isConnected, address, invoice, loadingInvoice, createInvoice])

  // Reset state when closed
  useEffect(() => {
    if (!open) {
      setSuccess(false)
      setLocalError(null)
    }
  }, [open])

  const handlePay = async () => {
    if (!invoice) return
    
    try {
      setLocalError(null)
      const result = await processPayment(invoice)
      if (result.status === 'confirmed') {
        setSuccess(true)
        setTimeout(() => {
          onSuccess(result.invoiceId)
          onOpenChange(false)
        }, 1500)
      }
    } catch (e) {
      // Error handling is inside hook, but we can also set local state if needed
    }
  }

  const error = localError || hookError

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Complete Your Analysis</DialogTitle>
          <DialogDescription>
            A payment of 0.10 USD₮0 is required to start the brand analysis.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col items-center gap-6 py-6">
          <div className="text-4xl font-bold text-slate-900">
            $0.10 <span className="text-lg font-medium text-slate-500">USD₮0</span>
          </div>

          <div className="w-full space-y-4">
            {!isConnected ? (
              <div className="flex justify-center">
                <ConnectButton />
              </div>
            ) : success ? (
              <Button className="w-full bg-green-600 hover:bg-green-700" disabled>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Payment Confirmed
              </Button>
            ) : (
              <Button 
                onClick={handlePay} 
                disabled={isProcessing || loadingInvoice || !invoice} 
                className="w-full text-lg h-12"
              >
                {isProcessing || loadingInvoice ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {loadingInvoice ? 'Generating Invoice...' : 'Processing Payment...'}
                  </>
                ) : (
                  'Sign & Pay'
                )}
              </Button>
            )}

            {error && (
              <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg text-center">
                {error}
              </div>
            )}
            
            <p className="text-xs text-center text-slate-400">
              Payments are processed securely via Plasma network.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
