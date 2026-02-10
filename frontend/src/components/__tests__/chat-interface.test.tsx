import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TooltipProvider } from '@/components/ui/tooltip'
import { ChatInterface } from '../chat-interface'
import type { Conversation } from '@/lib/store'

function AllProviders({ children }: { children: React.ReactNode }) {
  return <TooltipProvider delayDuration={0}>{children}</TooltipProvider>
}

const defaultModes = [
  { id: 'general', name: 'General', description: 'General-purpose', routing: 'best-fit' },
]
const defaultModels = [
  { id: 'llama3', name: 'Llama 3', provider: 'Ollama', type: 'ollama' as const, status: 'online' as const },
]

function renderChat(overrides: Partial<{
  conversation: Conversation | null
  onSendMessage: (content: string) => void
  isStreaming: boolean
}> = {}) {
  const props = {
    conversation: null,
    onSendMessage: jest.fn(),
    isStreaming: false,
    modes: defaultModes,
    models: defaultModels,
    selectedModeId: 'general',
    selectedModelId: '',
    onSelectMode: jest.fn(),
    onSelectModel: jest.fn(),
    agenticMode: true,
    onToggleAgenticMode: jest.fn(),
    ...overrides,
  }
  return render(
    <AllProviders>
      <ChatInterface {...props} />
    </AllProviders>
  )
}

describe('ChatInterface', () => {
  it('shows empty state when no conversation', () => {
    renderChat()
    expect(screen.getByText(/start a new conversation/i)).toBeInTheDocument()
    expect(screen.getByText(/select a conversation or create a new one/i)).toBeInTheDocument()
  })

  it('shows messages when conversation has messages', () => {
    const conv: Conversation = {
      id: 'conv-1',
      title: 'Test',
      projectId: 'proj-1',
      messages: [
        { id: 'm1', role: 'user', content: 'Hello', timestamp: new Date() },
        { id: 'm2', role: 'assistant', content: 'Hi there', timestamp: new Date() },
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    renderChat({ conversation: conv })
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByText('Hi there')).toBeInTheDocument()
  })

  it('has a send button and text input', () => {
    renderChat()
    const input = screen.getByPlaceholderText(/message.*@.*context/i)
    expect(input).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('does not call onSendMessage when input is empty and send clicked', async () => {
    const user = userEvent.setup()
    const onSendMessage = jest.fn()
    const conv: Conversation = {
      id: 'c1',
      title: 'T',
      projectId: 'p1',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    renderChat({ conversation: conv, onSendMessage })
    const sendBtn = screen.getByRole('button', { name: /send/i })
    await user.click(sendBtn)
    expect(onSendMessage).not.toHaveBeenCalled()
  })

  it('calls onSendMessage when user types and sends', async () => {
    const user = userEvent.setup()
    const onSendMessage = jest.fn()
    const conv: Conversation = {
      id: 'c1',
      title: 'T',
      projectId: 'p1',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    renderChat({ conversation: conv, onSendMessage })
    const input = screen.getByPlaceholderText(/message.*@.*context/i)
    await user.type(input, 'Hello')
    await user.click(screen.getByRole('button', { name: /send/i }))
    expect(onSendMessage).toHaveBeenCalledWith('Hello')
  })

  it('send button is disabled when isStreaming', () => {
    const conv: Conversation = {
      id: 'c1',
      title: 'T',
      projectId: 'p1',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    renderChat({ conversation: conv, isStreaming: true })
    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled()
  })
})
