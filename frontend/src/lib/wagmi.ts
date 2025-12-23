import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { http } from 'wagmi';
import { mainnet, sepolia } from 'wagmi/chains';
import { type Chain } from 'viem';

export const plasma = {
  id: 9745,
  name: 'Plasma',
  nativeCurrency: { name: 'Ether', symbol: 'ETH', decimals: 18 },
  rpcUrls: {
    default: { http: ['https://rpc.plasma.to'] },
  },
  blockExplorers: {
    default: { name: 'Plasma Explorer', url: 'https://explorer.plasma.to' },
  },
} as const satisfies Chain;

export const config = getDefaultConfig({
  appName: 'Brand Analytics',
  projectId: 'YOUR_PROJECT_ID', // Get one at https://cloud.walletconnect.com
  chains: [plasma, mainnet, sepolia],
  transports: {
    [plasma.id]: http(),
    [mainnet.id]: http(),
    [sepolia.id]: http(),
  },
  ssr: true, // If your dApp uses server side rendering (SSR)
});

