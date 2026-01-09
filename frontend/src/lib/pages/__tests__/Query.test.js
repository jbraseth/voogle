/**
 * Test suite for Query.svelte component
 *
 * NOTE: These tests require vitest + @testing-library/svelte to be installed.
 * See frontend/test-setup.md for installation instructions.
 *
 * These tests are designed to EXPOSE bugs in the Query component:
 * 1. Incorrect button onClick handler (calls function immediately)
 * 2. Missing null checks for qs prop
 * 3. Missing error handling for network failures
 * 4. Potential undefined access in reactive statements
 */

import { render, fireEvent, waitFor, screen } from '@testing-library/svelte'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Query from '../Query.svelte'

// Mock the API module
vi.mock('../../../api.js', () => ({
  API_URL: 'http://localhost:8080'
}))

// Mock the stores module
vi.mock('../../../stores.js', () => ({
  channels: {
    subscribe: vi.fn((cb) => {
      cb([])
      return () => {}
    })
  }
}))

describe('Query.svelte - Bug Detection Tests', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  it('should handle undefined qs prop without crashing', () => {
    /**
     * Expose: Line 11 - let query = qs.get("q")
     * If qs is undefined, this will crash with "Cannot read property 'get' of undefined"
     *
     * Expected to FAIL: Component doesn't check if qs exists before calling .get()
     */
    expect(() => {
      render(Query, { props: { qs: undefined } })
    }).not.toThrow()
  })

  it('should handle null qs prop without crashing', () => {
    /**
     * Expose: Same issue as above but with explicit null
     *
     * Expected to FAIL: Component doesn't handle null qs
     */
    expect(() => {
      render(Query, { props: { qs: null } })
    }).not.toThrow()
  })

  it('should handle qs without query parameter', () => {
    /**
     * Expose: What happens when qs.get("q") returns null?
     *
     * Expected to potentially FAIL: May not handle null query value gracefully
     */
    const mockQs = {
      get: vi.fn(() => null)
    }

    const { container } = render(Query, { props: { qs: mockQs } })
    expect(container).toBeTruthy()
  })

  it('should NOT call doQuery immediately when button is rendered', async () => {
    /**
     * Expose: Line 91 - on:click={doQuery(query)}
     * This is WRONG! It calls doQuery immediately during render, not on click.
     * Should be: on:click={() => doQuery(query)}
     *
     * Expected to FAIL: Button handler is incorrectly configured
     */
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve([])
      })
    )

    const mockQs = {
      get: vi.fn(() => 'test query')
    }

    const { container } = render(Query, { props: { qs: mockQs } })

    // Wait for initial mount query to complete
    await waitFor(() => expect(global.fetch).toHaveBeenCalled())
    const initialCallCount = global.fetch.mock.calls.length

    // Find and click the search button
    const searchButton = container.querySelector('button')
    expect(searchButton).toBeTruthy()

    await fireEvent.click(searchButton)

    // After click, fetch should be called ONE more time
    // If the bug exists, it may have already been called during render
    expect(global.fetch.mock.calls.length).toBe(initialCallCount + 1)
  })

  it('should handle network error gracefully', async () => {
    /**
     * Expose: No error handling in doQuery function
     * If fetch fails, the component may show spinner forever or crash
     *
     * Expected to FAIL: No error state handling
     */
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error')))

    const mockQs = {
      get: vi.fn(() => null)
    }

    const { container } = render(Query, { props: { qs: mockQs } })

    const textarea = container.querySelector('textarea')
    await fireEvent.input(textarea, { target: { value: 'test query' } })
    await fireEvent.keyPress(textarea, { key: 'Enter' })

    // Should show error message, not spinner forever
    await waitFor(() => {
      const errorMessage = screen.queryByText(/error|failed|wrong/i)
      expect(errorMessage).toBeTruthy()
    }, { timeout: 2000 })
  })

  it('should handle empty queryResults without crashing maxSim calculation', async () => {
    /**
     * Expose: Line 72 - maxSim = queryResults && queryResults.length > 0 ? ...
     * If queryResults becomes empty array after being populated, may cause issues
     *
     * Expected to potentially FAIL: Reactive statement may not handle transitions properly
     */
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve([])
      })
    )

    const mockQs = {
      get: vi.fn(() => 'test')
    }

    const { component } = render(Query, { props: { qs: mockQs } })

    // Wait for query to complete with empty results
    await waitFor(() => expect(global.fetch).toHaveBeenCalled())

    // Component should not crash with empty results
    expect(component).toBeTruthy()
  })

  it('should handle fetch returning non-JSON gracefully', async () => {
    /**
     * Expose: No error handling for malformed responses
     * If API returns HTML error page, .json() will fail
     *
     * Expected to FAIL: No try-catch around response parsing
     */
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.reject(new Error('Unexpected token < in JSON'))
      })
    )

    const mockQs = {
      get: vi.fn(() => null)
    }

    const { container } = render(Query, { props: { qs: mockQs } })

    const textarea = container.querySelector('textarea')
    await fireEvent.input(textarea, { target: { value: 'test' } })
    await fireEvent.keyPress(textarea, { key: 'Enter' })

    // Should not crash the component
    await waitFor(() => {
      expect(container).toBeTruthy()
    })
  })

  it('should handle empty channels array in select dropdown', () => {
    /**
     * Expose: Lines 87-89 - What if $channels is empty/undefined?
     *
     * Expected to PASS: Svelte each block handles empty arrays gracefully
     */
    const mockQs = {
      get: vi.fn(() => null)
    }

    const { container } = render(Query, { props: { qs: mockQs } })

    const select = container.querySelector('select')
    expect(select).toBeTruthy()

    // Should have at least the "All channels" option
    const options = select.querySelectorAll('option')
    expect(options.length).toBeGreaterThanOrEqual(1)
  })

  it('should validate query before executing', async () => {
    /**
     * Expose: Line 19 - if (query.length > 0)
     * But what if query is null or undefined instead of empty string?
     *
     * Expected to potentially FAIL: Type check instead of truthy check
     */
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve([])
      })
    )

    const mockQs = {
      get: vi.fn(() => null)
    }

    const { container } = render(Query, { props: { qs: mockQs } })

    // Try to trigger query with null/undefined
    const button = container.querySelector('button')
    await fireEvent.click(button)

    // Should not make API call if query is invalid
    expect(global.fetch).not.toHaveBeenCalledWith(
      expect.stringContaining('/media/query')
    )
  })

  it('should handle player scrolling when player element not found', async () => {
    /**
     * Expose: Line 60 - player.scrollIntoView()
     * What if player element hasn't rendered yet?
     *
     * Expected to potentially FAIL: No null check before scrollIntoView
     */
    const mockQs = {
      get: vi.fn(() => null)
    }

    const { component } = render(Query, { props: { qs: mockQs } })

    // Trigger click event that calls scrollIntoView
    const clickData = {
      detail: {
        episode: { id: '123' },
        channel: { id: '456' },
        time: 100
      }
    }

    // This should not crash even if player element doesn't exist
    expect(() => {
      component.$$.ctx[component.$$.props['click']](clickData)
    }).not.toThrow()
  })

  it('should properly clean up history state on component destroy', () => {
    /**
     * Expose: Line 22 - history.replaceState(history.state, "", "?q=" + query)
     * If component is destroyed during query, may leave bad history state
     *
     * Expected to potentially FAIL: No cleanup of history manipulation
     */
    const mockQs = {
      get: vi.fn(() => 'test')
    }

    const { unmount } = render(Query, { props: { qs: mockQs } })

    // Unmount during potential async operation
    expect(() => unmount()).not.toThrow()
  })
})
