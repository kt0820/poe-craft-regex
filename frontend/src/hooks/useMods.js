/**
 * useMods.js
 * ----------
 * Manages mod families, selection, regex generation, search,
 * and accordion expand/collapse (only one family open at a time).
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import { fetchModsBySlot, generateRegex } from '../services/api'

export const TAG_ORDER  = ['prefix', 'suffix', 'other']
export const TAG_LABELS = { prefix: 'Prefix', suffix: 'Suffix', other: 'Other' }

export function useMods(selectedSlot) {
  const [families, setFamilies]         = useState([])
  const [selectedIds, setSelectedIds]   = useState(new Set())
  const [expandedKey, setExpandedKey]   = useState(null)  // only one at a time
  const [regex, setRegex]               = useState('')
  const [modCount, setModCount]         = useState(0)
  const [hasNonUnique, setHasNonUnique] = useState(false)
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState(null)
  const [copied, setCopied]             = useState(false)
  const [search, setSearch]             = useState('')

  // Load families when slot changes
  useEffect(() => {
    setLoading(true)
    setError(null)
    setSelectedIds(new Set())
    setExpandedKey(null)
    setRegex('')
    setModCount(0)
    setSearch('')

    fetchModsBySlot(selectedSlot)
      .then(setFamilies)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [selectedSlot])

  // Regenerate regex when selection changes
  useEffect(() => {
    if (selectedIds.size === 0) {
      setRegex('')
      setModCount(0)
      setHasNonUnique(false)
      return
    }
    generateRegex([...selectedIds])
      .then(data => {
        setRegex(data.regex)
        setModCount(data.mod_count)
        setHasNonUnique(data.has_non_unique)
      })
      .catch(err => setError(err.message))
  }, [selectedIds])

  const toggleMod = useCallback((modId) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      next.has(modId) ? next.delete(modId) : next.add(modId)
      return next
    })
  }, [])

  // Accordion: clicking a family opens it and closes any other open family
  const toggleFamily = useCallback((familyKey) => {
    setExpandedKey(prev => prev === familyKey ? null : familyKey)
  }, [])

  const clearSelection = useCallback(() => setSelectedIds(new Set()), [])

  const copyToClipboard = useCallback(() => {
    if (!regex) return
    navigator.clipboard.writeText(regex).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }, [regex])

  // Filter families by search — when searching, expand all matching families
  const filteredFamilies = useMemo(() => {
    if (!search.trim()) return families
    const q = search.toLowerCase()
    return families
      .map(fam => ({
        ...fam,
        mods: fam.mods.filter(m => m.name.toLowerCase().includes(q)),
      }))
      .filter(fam => fam.mods.length > 0)
  }, [families, search])

  // Group by tag
  const groupedFamilies = useMemo(() => {
    return TAG_ORDER.reduce((acc, tag) => {
      const group = filteredFamilies.filter(f => f.tag === tag)
      if (group.length > 0) acc[tag] = group
      return acc
    }, {})
  }, [filteredFamilies])

  // During search, treat all matching families as "expanded"
  const isExpanded = useCallback((familyKey) => {
    if (search.trim()) return true   // show all tiers when searching
    return expandedKey === familyKey
  }, [expandedKey, search])

  return {
    groupedFamilies,
    selectedIds,
    isExpanded,
    regex,
    modCount,
    hasNonUnique,
    loading,
    error,
    copied,
    search,
    setSearch,
    toggleMod,
    toggleFamily,
    clearSelection,
    copyToClipboard,
  }
}
