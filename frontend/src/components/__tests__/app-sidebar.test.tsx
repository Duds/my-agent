import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AppSidebar } from '../app-sidebar'
import type { Project, Conversation, AgentProcess, CronJob, Automation } from '@/lib/store'

jest.mock('@/lib/api-client', () => ({
  api: {
    getVaultStatus: jest.fn().mockResolvedValue({ initialized: false, locked: true }),
  },
}))

const defaultProjects: Project[] = [
  { id: 'proj-1', name: 'Default', color: 'hsl(217, 92%, 60%)', conversationIds: [] },
]

const defaultConversations: Conversation[] = []

const defaultAgentProcesses: AgentProcess[] = []
const defaultCronJobs: CronJob[] = []
const defaultAutomations: Automation[] = []

async function renderSidebar(overrides: Partial<{
  projects: Project[]
  onCreateProject: (name: string, color?: string) => Promise<void>
  onPatchProject: (id: string, updates: { name?: string; color?: string }) => Promise<void>
}> = {}) {
  const props = {
    projects: defaultProjects,
    conversations: defaultConversations,
    activeConversationId: null,
    activeProjectId: null,
    onSelectConversation: jest.fn(),
    onSelectProject: jest.fn(),
    onNewConversation: jest.fn(),
    collapsed: false,
    agentProcesses: defaultAgentProcesses,
    cronJobs: defaultCronJobs,
    automations: defaultAutomations,
    ...overrides,
  }
  const result = render(<AppSidebar {...props} />)
  await act(async () => {
    await Promise.resolve()
  })
  return result
}

describe('AppSidebar', () => {
  it('renders Chats and Agents tabs', async () => {
    await renderSidebar()
    expect(screen.getByRole('tab', { name: /chats/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /agents/i })).toBeInTheDocument()
  })

  it('shows New conversation button in Chats tab', async () => {
    await renderSidebar()
    expect(screen.getByRole('button', { name: /new conversation/i })).toBeInTheDocument()
  })

  it('shows New project button when onCreateProject is provided', async () => {
    await renderSidebar({ onCreateProject: jest.fn() })
    expect(screen.getByRole('button', { name: /new project/i })).toBeInTheDocument()
  })

  it('does not show New project button when onCreateProject is not provided', async () => {
    await renderSidebar()
    expect(screen.queryByRole('button', { name: /new project/i })).not.toBeInTheDocument()
  })

  it('displays project names', async () => {
    await renderSidebar({ projects: [...defaultProjects, { id: 'proj-2', name: 'Work', color: 'hsl(142, 76%, 36%)', conversationIds: [] }] })
    expect(screen.getByText('Default')).toBeInTheDocument()
    expect(screen.getByText('Work')).toBeInTheDocument()
  })

  it('opens new project dialog when New project is clicked', async () => {
    const user = userEvent.setup()
    await renderSidebar({ onCreateProject: jest.fn() })
    await user.click(screen.getByRole('button', { name: /new project/i }))
    expect(screen.getByRole('dialog', { name: /new project/i })).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/project name/i)).toBeInTheDocument()
  })

  it('calls onNewConversation when New conversation is clicked', async () => {
    const user = userEvent.setup()
    const onNewConversation = jest.fn()
    await renderSidebar({ onNewConversation })
    await user.click(screen.getByRole('button', { name: /new conversation/i }))
    expect(onNewConversation).toHaveBeenCalledTimes(1)
  })

  it('switches to Agents tab and shows agents content', async () => {
    const user = userEvent.setup()
    await renderSidebar()
    await user.click(screen.getByRole('tab', { name: /agents/i }))
    expect(screen.getByText(/background agents/i)).toBeInTheDocument()
  })
})
