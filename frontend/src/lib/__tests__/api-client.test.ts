/**
 * API client tests with mocked fetch.
 */

import { api } from '../api-client'

const originalFetch = globalThis.fetch

beforeEach(() => {
  globalThis.fetch = jest.fn()
})

afterEach(() => {
  globalThis.fetch = originalFetch
})

function mockResolve<T>(data: T) {
  ;(globalThis.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve(data),
  })
}

function mockReject(status: number, detail: string) {
  ;(globalThis.fetch as jest.Mock).mockResolvedValueOnce({
    ok: false,
    status,
    statusText: 'Error',
    json: () => Promise.resolve({ detail }),
  })
}

describe('api-client', () => {
  describe('getProjects', () => {
    it('returns projects from API', async () => {
      const projects = [{ id: 'proj-1', name: 'Default', color: 'hsl(0,0%,50%)', conversationIds: [] }]
      mockResolve(projects)
      const result = await api.getProjects()
      expect(result).toEqual(projects)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projects'),
        expect.any(Object)
      )
    })
  })

  describe('createProject', () => {
    it('POSTs name and color and returns created project', async () => {
      const created = { id: 'proj-2', name: 'Work', color: 'hsl(142, 76%, 36%)', conversationIds: [] }
      mockResolve(created)
      const result = await api.createProject({ name: 'Work', color: 'hsl(142, 76%, 36%)' })
      expect(result).toEqual(created)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projects'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'Work', color: 'hsl(142, 76%, 36%)' }),
        })
      )
    })
  })

  describe('patchProject', () => {
    it('PATCHes project and returns updated project', async () => {
      const updated = { id: 'proj-1', name: 'Renamed', color: 'hsl(199, 89%, 48%)', conversationIds: [] }
      mockResolve(updated)
      const result = await api.patchProject('proj-1', { name: 'Renamed' })
      expect(result).toEqual(updated)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projects/proj-1'),
        expect.objectContaining({ method: 'PATCH' })
      )
    })
  })

  describe('getHealth', () => {
    it('returns health status', async () => {
      mockResolve({ status: 'healthy', service: 'Secure Personal Agentic Platform' })
      const result = await api.getHealth()
      expect(result.status).toBe('healthy')
      expect(globalThis.fetch).toHaveBeenCalledWith(expect.stringContaining('/health'), expect.any(Object))
    })
  })

  describe('getCronJobs', () => {
    it('returns cron jobs list', async () => {
      const jobs = [{ id: 'cron-1', name: 'Daily', schedule: '0 9 * * *', status: 'active', lastRun: null, nextRun: '2026-02-10T09:00:00Z', description: '', projectId: undefined }]
      mockResolve(jobs)
      const result = await api.getCronJobs()
      expect(result).toEqual(jobs)
      expect(globalThis.fetch).toHaveBeenCalledWith(expect.stringContaining('/api/cron-jobs'), expect.any(Object))
    })
  })

  describe('getAutomations', () => {
    it('returns automations list', async () => {
      const automations = [{ id: 'auto-1', name: 'Watch', trigger: 'file.created', status: 'active', lastTriggered: null, runsToday: 0, description: '', type: 'watch' as const }]
      mockResolve(automations)
      const result = await api.getAutomations()
      expect(result).toEqual(automations)
      expect(globalThis.fetch).toHaveBeenCalledWith(expect.stringContaining('/api/automations'), expect.any(Object))
    })
  })

  describe('error handling', () => {
    it('throws with API detail when response not ok', async () => {
      mockReject(404, 'Project not found')
      await expect(api.getProjects()).rejects.toThrow('Project not found')
    })

    it('throws with status text when detail missing', async () => {
      ;(globalThis.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({}),
      })
      await expect(api.getProjects()).rejects.toThrow(/500|Internal Server Error/)
    })
  })
})
