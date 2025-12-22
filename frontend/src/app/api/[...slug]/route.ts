import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

async function proxyRequest(
  request: NextRequest,
  slug: string[],
  method: string
): Promise<NextResponse> {
  const pathname = slug.join('/')
  const backendUrl = new URL(`/api/${pathname}`, BACKEND_URL)

  request.nextUrl.searchParams.forEach((value, key) => {
    backendUrl.searchParams.set(key, value)
  })

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  const authHeader = request.headers.get('Authorization')
  if (authHeader) {
    headers['Authorization'] = authHeader
  }

  const fetchOptions: RequestInit = {
    method,
    headers,
  }

  if (method !== 'GET' && method !== 'HEAD') {
    try {
      const body = await request.text()
      if (body) {
        fetchOptions.body = body
      }
    } catch {
    }
  }

  try {
    const response = await fetch(backendUrl.toString(), fetchOptions)

    const contentType = response.headers.get('content-type')

    if (contentType?.includes('application/pdf')) {
      const pdfBuffer = await response.arrayBuffer()
      return new NextResponse(pdfBuffer, {
        status: response.status,
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': response.headers.get('content-disposition') || 'attachment',
        },
      })
    }

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to connect to backend', detail: String(error) },
      { status: 502 }
    )
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string[] }> }
): Promise<NextResponse> {
  const { slug } = await params
  return proxyRequest(request, slug, 'GET')
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string[] }> }
): Promise<NextResponse> {
  const { slug } = await params
  return proxyRequest(request, slug, 'POST')
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string[] }> }
): Promise<NextResponse> {
  const { slug } = await params
  return proxyRequest(request, slug, 'PUT')
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string[] }> }
): Promise<NextResponse> {
  const { slug } = await params
  return proxyRequest(request, slug, 'DELETE')
}
