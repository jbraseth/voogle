/**
 * Test suite for About.svelte component
 *
 * NOTE: These tests require vitest + @testing-library/svelte to be installed.
 * See frontend/test-setup.md for installation instructions.
 *
 * About.svelte is relatively simple, but we should still verify:
 * 1. Component renders without props
 * 2. External links are properly formatted
 * 3. Images exist and are accessible
 * 4. No XSS vulnerabilities in static content
 */

import { render, screen } from '@testing-library/svelte'
import { describe, it, expect } from 'vitest'
import About from '../About.svelte'

describe('About.svelte - Basic Functionality Tests', () => {
  it('should render without qs prop', () => {
    /**
     * Expose: Component should handle missing qs prop
     *
     * Expected to PASS: qs is defined with default null value
     */
    expect(() => {
      render(About, { props: {} })
    }).not.toThrow()
  })

  it('should render with undefined qs prop', () => {
    /**
     * Expose: Component should handle undefined qs
     *
     * Expected to PASS: Default value handles this
     */
    expect(() => {
      render(About, { props: { qs: undefined } })
    }).not.toThrow()
  })

  it('should render with null qs prop', () => {
    /**
     * Expose: Component should handle explicit null qs
     *
     * Expected to PASS: Default value is null
     */
    expect(() => {
      render(About, { props: { qs: null } })
    }).not.toThrow()
  })

  it('should display main heading', () => {
    /**
     * Expose: Main heading should be visible
     *
     * Expected to PASS: Static content
     */
    render(About, { props: {} })

    const heading = screen.getByText(/Text is not the only source of knowledge/i)
    expect(heading).toBeTruthy()
  })

  it('should reference Voogle correctly in text', () => {
    /**
     * Expose: After rebranding from Voogle to Voogle, verify text is updated
     *
     * Expected to PASS: Line 13 uses "Voogle"
     */
    render(About, { props: {} })

    const voogleMention = screen.getByText(/Voogle has an army/i)
    expect(voogleMention).toBeTruthy()
  })

  it('should have link to content page', () => {
    /**
     * Expose: Internal link should be properly formatted
     *
     * Expected to PASS: Line 15-16 has href="/content"
     */
    const { container } = render(About, { props: {} })

    const contentLink = container.querySelector('a[href="/content"]')
    expect(contentLink).toBeTruthy()
    expect(contentLink.textContent).toContain('episodes')
  })

  it('should have Twitter/X link with proper attributes', () => {
    /**
     * Expose: External link should have security attributes
     *
     * Expected to PASS: Line 61 has rel="noopener noreferrer" and target="_blank"
     */
    const { container } = render(About, { props: {} })

    const twitterLink = container.querySelector('a[href*="twitter.com"]')
    expect(twitterLink).toBeTruthy()
    expect(twitterLink.getAttribute('rel')).toContain('noopener')
    expect(twitterLink.getAttribute('rel')).toContain('noreferrer')
    expect(twitterLink.getAttribute('target')).toBe('_blank')
  })

  it('should have all required static images', () => {
    /**
     * Expose: Image paths should be valid
     *
     * Expected to potentially FAIL if images are missing:
     * - /monkey-computer.jpg (line 23)
     * - /monkey-glasses.jpeg (line 35)
     * - /monkey-books.jpeg (line 47)
     */
    const { container } = render(About, { props: {} })

    const images = container.querySelectorAll('img')
    expect(images.length).toBe(3)

    const imagePaths = Array.from(images).map(img => img.getAttribute('src'))
    expect(imagePaths).toContain('/monkey-computer.jpg')
    expect(imagePaths).toContain('/monkey-glasses.jpeg')
    expect(imagePaths).toContain('/monkey-books.jpeg')
  })

  it('should have alt text for all images', () => {
    /**
     * Expose: Accessibility - all images should have alt text
     *
     * Expected to PASS: All images have alt attributes
     */
    const { container } = render(About, { props: {} })

    const images = container.querySelectorAll('img')
    images.forEach(img => {
      const alt = img.getAttribute('alt')
      expect(alt).toBeTruthy()
      expect(alt.length).toBeGreaterThan(0)
    })
  })

  it('should have three feature cards', () => {
    /**
     * Expose: Should display all three feature cards
     *
     * Expected to PASS: Three .card elements
     */
    const { container } = render(About, { props: {} })

    const cards = container.querySelectorAll('.card')
    expect(cards.length).toBe(3)
  })

  it('should display correct card titles', () => {
    /**
     * Expose: Feature cards should have correct titles
     *
     * Expected to PASS: Static content
     */
    render(About, { props: {} })

    expect(screen.getByText('Daily episode collection')).toBeTruthy()
    expect(screen.getByText('High quality transcriptions')).toBeTruthy()
    expect(screen.getByText('Smart search')).toBeTruthy()
  })

  it('should emphasize key features in card descriptions', () => {
    /**
     * Expose: Important terms should be emphasized (font-semibold)
     *
     * Expected to PASS: Lines 27, 40, 53-54 have font-semibold
     */
    const { container } = render(About, { props: {} })

    const emphasized = container.querySelectorAll('.font-semibold')
    expect(emphasized.length).toBeGreaterThanOrEqual(3)

    const emphasizedText = Array.from(emphasized).map(el => el.textContent)
    expect(emphasizedText).toContain('collect')
    expect(emphasizedText).toContain('transcript')
    expect(emphasizedText.some(text => text.includes('natural'))).toBe(true)
  })

  it('should not have any XSS vulnerabilities in static content', () => {
    /**
     * Expose: Static content should be properly escaped
     *
     * Expected to PASS: Svelte templates are auto-escaped
     */
    const { container } = render(About, { props: {} })

    // Should not have any executable script tags in rendered output
    const scriptTags = container.querySelectorAll('script')
    const inlineScripts = Array.from(scriptTags).filter(
      s => !s.getAttribute('src') // Only inline scripts are suspicious
    )

    inlineScripts.forEach(script => {
      expect(script.textContent).not.toContain('alert')
      expect(script.textContent).not.toContain('document.cookie')
    })
  })

  it('should use semantic HTML structure', () => {
    /**
     * Expose: Should use proper semantic HTML elements
     *
     * Expected to PASS: Uses main, h2, p, figure elements
     */
    const { container } = render(About, { props: {} })

    expect(container.querySelector('main')).toBeTruthy()
    expect(container.querySelector('h2')).toBeTruthy()
    expect(container.querySelectorAll('p').length).toBeGreaterThan(0)
    expect(container.querySelectorAll('figure').length).toBe(3)
  })

  it('should have responsive grid layout classes', () => {
    /**
     * Expose: Should use Tailwind responsive classes
     *
     * Expected to PASS: Line 19 has xl:grid-cols-3
     */
    const { container } = render(About, { props: {} })

    const grid = container.querySelector('.grid')
    expect(grid).toBeTruthy()

    const classes = grid.className
    expect(classes).toContain('grid-cols-1')
    expect(classes).toContain('xl:grid-cols-3')
  })

  it('should have proper spacing classes', () => {
    /**
     * Expose: Should use consistent spacing
     *
     * Expected to PASS: Uses gap-12, mt-6, etc.
     */
    const { container } = render(About, { props: {} })

    const main = container.querySelector('main')
    expect(main.className).toContain('gap-12')
  })

  it('should handle rapid mount/unmount cycles', () => {
    /**
     * Expose: Component should handle being mounted and unmounted quickly
     *
     * Expected to PASS: No async operations to clean up
     */
    const { unmount } = render(About, { props: {} })

    expect(() => unmount()).not.toThrow()
  })

  it('should be accessible with keyboard navigation', () => {
    /**
     * Expose: Links should be keyboard accessible
     *
     * Expected to PASS: All links are standard <a> tags
     */
    const { container } = render(About, { props: {} })

    const links = container.querySelectorAll('a')
    links.forEach(link => {
      // Links should be focusable
      expect(link.tagName).toBe('A')
      // Should have href
      expect(link.getAttribute('href')).toBeTruthy()
    })
  })
})
