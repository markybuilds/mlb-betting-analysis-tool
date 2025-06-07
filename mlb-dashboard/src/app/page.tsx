'use client'

import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RefreshCw, TrendingUp, Target, Users, Check, Filter, ChevronDown, X } from 'lucide-react'
import { cn, formatPercentage, formatDecimal, getConfidenceBadgeColor, getRecommendationColor } from '@/lib/utils'

interface PlayerProjection {
  PLAYER: string
  POS: string
  TEAM: string
  GAME: string
  INN: string
  K: string
  HA: string
  ER: string
  BBI: string
  RBI: string
  R: string
  H: string
}

interface BatterAnalysis {
  PLAYER: string
  TEAM: string
  GAME: string
  POS: string
  H_PROJECTION: number
  OPTIMAL_ALT_LINE: number
  EDGE: number
  EDGE_PERCENTAGE: number
  CONFIDENCE: string
  RECOMMENDATION: string
}

interface PitcherAnalysis {
  PLAYER: string
  TEAM: string
  GAME: string
  K_PROJECTION: number
  OPTIMAL_ALT_LINE: number
  EDGE: number
  EDGE_PERCENTAGE: number
  CONFIDENCE: string
  RECOMMENDATION: string
}

export default function MLBDashboard() {
  const [playerProjections, setPlayerProjections] = useState<PlayerProjection[]>([])
  const [batterAnalysis, setBatterAnalysis] = useState<BatterAnalysis[]>([])
  const [pitcherAnalysis, setPitcherAnalysis] = useState<PitcherAnalysis[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string>('')
  const [selectedGames, setSelectedGames] = useState<string[]>([])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load player projections
      const projectionsResponse = await fetch('/api/data/projections')
      if (projectionsResponse.ok) {
        const projections = await projectionsResponse.json()
        setPlayerProjections(projections)
      }

      // Load batter analysis
      const batterResponse = await fetch('/api/data/batter-analysis')
      if (batterResponse.ok) {
        const batters = await batterResponse.json()
        setBatterAnalysis(batters)
      }

      // Load pitcher analysis
      const pitcherResponse = await fetch('/api/data/pitcher-analysis')
      if (pitcherResponse.ok) {
        const pitchers = await pitcherResponse.json()
        setPitcherAnalysis(pitchers)
      }

      setLastUpdated(new Date().toLocaleString())
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const refreshData = async () => {
    setUpdating(true)
    try {
      console.log('Starting data refresh...')
      const response = await fetch('/api/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const result = await response.json()
      
      if (result.success) {
        console.log('Data update successful:', result.message)
        // After successful update, reload the data
        await loadData()
      } else {
        console.error('Data update failed:', result.message)
        alert(`Data update failed: ${result.message}`)
      }
    } catch (error) {
      console.error('Error updating data:', error)
      alert('Error updating data. Please try again.')
    } finally {
      setUpdating(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Get unique games from all data sources
  const allGames = Array.from(new Set([
    ...playerProjections.map(p => p.GAME),
    ...batterAnalysis.map(b => b.GAME),
    ...pitcherAnalysis.map(p => p.GAME)
  ])).filter(game => game && game !== '-').sort()

  // Filter data based on selected games
  const filteredPlayerProjections = selectedGames.length === 0 
    ? playerProjections 
    : playerProjections.filter(p => selectedGames.includes(p.GAME))

  const filteredBatterAnalysis = selectedGames.length === 0 
    ? batterAnalysis 
    : batterAnalysis.filter(b => selectedGames.includes(b.GAME))

  const filteredPitcherAnalysis = selectedGames.length === 0 
    ? pitcherAnalysis 
    : pitcherAnalysis.filter(p => selectedGames.includes(p.GAME))

  const topBatterOpportunities = filteredBatterAnalysis
    .filter(b => b.EDGE_PERCENTAGE > 0)
    .sort((a, b) => {
      // First sort by confidence level (recommended bets first)
      const confidenceOrder = { 'High': 3, 'Medium': 2, 'Low': 1, 'Avoid': 0 }
      const confidenceDiff = (confidenceOrder[b.CONFIDENCE] || 0) - (confidenceOrder[a.CONFIDENCE] || 0)
      if (confidenceDiff !== 0) return confidenceDiff
      
      // Then sort by edge percentage within same confidence level
      return b.EDGE_PERCENTAGE - a.EDGE_PERCENTAGE
    })
    .slice(0, 5)

  const topPitcherOpportunities = filteredPitcherAnalysis
    .filter(p => p.CONFIDENCE === 'High' || p.CONFIDENCE === 'Medium')
    .sort((a, b) => b.EDGE_PERCENTAGE - a.EDGE_PERCENTAGE)
    .slice(0, 5)

  const handleGameFilterChange = (game: string) => {
    if (game === 'all') {
      setSelectedGames([])
    } else {
      setSelectedGames(prev => {
        if (prev.includes(game)) {
          // Remove game if already selected
          return prev.filter(g => g !== game)
        } else {
          // Add game if not selected
          return [...prev, game]
        }
      })
    }
  }

  const handleSelectAllGames = () => {
    setSelectedGames([])
  }

  const handleClearSelection = () => {
    setSelectedGames([])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">MLB Analysis Dashboard</h1>
              <p className="text-slate-300">Real-time player projections and betting analysis</p>
            </div>
            <div className="flex items-center gap-4">
              {/* Game Filter */}
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-slate-300" />
                <div className="relative">
                  <Select>
                    <SelectTrigger className="w-64 bg-slate-800 border-slate-600 text-white">
                      <div className="flex items-center justify-between w-full">
                        <span className="text-sm">
                          {selectedGames.length === 0 
                            ? 'All Games' 
                            : selectedGames.length === 1 
                            ? selectedGames[0]
                            : `${selectedGames.length} games selected`
                          }
                        </span>
                        <ChevronDown className="h-4 w-4 opacity-50" />
                      </div>
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-600 w-64">
                      {/* All Games Option */}
                      <div 
                        className="flex items-center gap-2 px-3 py-2 text-white hover:bg-slate-700 cursor-pointer"
                        onClick={handleSelectAllGames}
                      >
                        <div className={cn(
                          "w-4 h-4 border border-slate-400 rounded flex items-center justify-center",
                          selectedGames.length === 0 && "bg-blue-600 border-blue-600"
                        )}>
                          {selectedGames.length === 0 && <Check className="h-3 w-3 text-white" />}
                        </div>
                        <span>All Games</span>
                      </div>
                      
                      {/* Individual Game Options */}
                      {allGames.map(game => (
                        <div 
                          key={game}
                          className="flex items-center gap-2 px-3 py-2 text-white hover:bg-slate-700 cursor-pointer"
                          onClick={() => handleGameFilterChange(game)}
                        >
                          <div className={cn(
                            "w-4 h-4 border border-slate-400 rounded flex items-center justify-center",
                            selectedGames.includes(game) && "bg-blue-600 border-blue-600"
                          )}>
                            {selectedGames.includes(game) && <Check className="h-3 w-3 text-white" />}
                          </div>
                          <span>{game}</span>
                        </div>
                      ))}
                      
                      {/* Clear Selection */}
                      {selectedGames.length > 0 && (
                        <div className="border-t border-slate-600 mt-2 pt-2">
                          <div 
                            className="flex items-center gap-2 px-3 py-2 text-red-400 hover:bg-slate-700 cursor-pointer"
                            onClick={handleClearSelection}
                          >
                            <X className="h-4 w-4" />
                            <span>Clear Selection</span>
                          </div>
                        </div>
                      )}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <button
                onClick={refreshData}
                disabled={loading || updating}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white rounded-lg transition-colors"
              >
                <RefreshCw className={cn('h-4 w-4', (loading || updating) && 'animate-spin')} />
                {updating ? 'Updating...' : 'Refresh Data'}
              </button>
            </div>
          </div>
          {lastUpdated && (
            <p className="text-sm text-slate-400">Last updated: {lastUpdated}</p>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Total Players</CardTitle>
              <Users className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{filteredPlayerProjections.length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Batter Opportunities</CardTitle>
              <Target className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{filteredBatterAnalysis.length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Pitcher Opportunities</CardTitle>
              <TrendingUp className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{filteredPitcherAnalysis.length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">High Confidence</CardTitle>
              <TrendingUp className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {[...filteredBatterAnalysis, ...filteredPitcherAnalysis].filter(item => item.CONFIDENCE === 'High').length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50 border-slate-700">
            <TabsTrigger value="overview" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-slate-300">
              Overview
            </TabsTrigger>
            <TabsTrigger value="projections" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-slate-300">
              Player Projections
            </TabsTrigger>
            <TabsTrigger value="batters" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-slate-300">
              Batter Analysis
            </TabsTrigger>
            <TabsTrigger value="pitchers" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-slate-300">
              Pitcher Analysis
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Batter Opportunities */}
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Top Batter Opportunities</CardTitle>
                  <CardDescription className="text-slate-400">
                    Highest edge percentage bets for batters
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {topBatterOpportunities.map((batter, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium text-white">{batter.PLAYER}</p>
                          <p className="text-sm text-slate-400">{batter.TEAM} - {batter.GAME}</p>
                          <div className="flex gap-2 mt-1">
                            <Badge className={cn(
                              "text-xs",
                              getRecommendationColor(batter.RECOMMENDATION)
                            )}>
                              {batter.RECOMMENDATION}
                            </Badge>
                            <Badge variant="outline" className="text-xs text-slate-300 border-slate-500">
                              {batter.H_PROJECTION} H
                            </Badge>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={getConfidenceBadgeColor(batter.CONFIDENCE)}>
                            {batter.CONFIDENCE}
                          </Badge>
                          <p className="text-sm text-green-400 mt-1">
                            {formatPercentage(batter.EDGE_PERCENTAGE)} edge
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Top Pitcher Opportunities */}
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Top Pitcher Opportunities</CardTitle>
                  <CardDescription className="text-slate-400">
                    Highest edge percentage bets for pitchers
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {topPitcherOpportunities.map((pitcher, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium text-white">{pitcher.PLAYER}</p>
                          <p className="text-sm text-slate-400">{pitcher.TEAM} - {pitcher.GAME}</p>
                          <div className="flex gap-2 mt-1">
                            <Badge className={cn(
                              "text-xs",
                              getRecommendationColor(pitcher.RECOMMENDATION)
                            )}>
                              {pitcher.RECOMMENDATION}
                            </Badge>
                            <Badge variant="outline" className="text-xs text-slate-300 border-slate-500">
                              {pitcher.K_PROJECTION} K
                            </Badge>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={getConfidenceBadgeColor(pitcher.CONFIDENCE)}>
                            {pitcher.CONFIDENCE}
                          </Badge>
                          <p className="text-sm text-green-400 mt-1">
                            {formatPercentage(pitcher.EDGE_PERCENTAGE)} edge
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Player Projections Tab */}
          <TabsContent value="projections">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Player Projections</CardTitle>
                <CardDescription className="text-slate-400">
                  Complete player statistics projections
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left p-2 text-slate-300">Player</th>
                        <th className="text-left p-2 text-slate-300">Pos</th>
                        <th className="text-left p-2 text-slate-300">Team</th>
                        <th className="text-left p-2 text-slate-300">Game</th>
                        <th className="text-left p-2 text-slate-300">RBI</th>
                        <th className="text-left p-2 text-slate-300">R</th>
                        <th className="text-left p-2 text-slate-300">H</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredPlayerProjections
                        .sort((a, b) => {
                          const aH = a.H !== '-' ? parseFloat(a.H) : 0
                          const bH = b.H !== '-' ? parseFloat(b.H) : 0
                          return bH - aH
                        })
                        .slice(0, 50)
                        .map((player, index) => (
                        <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/25">
                          <td className="p-2 text-white font-medium">
                            <div className="flex items-center gap-2">
                              {player.H !== '-' && parseFloat(player.H) >= 1.10 && (
                                <Check className="h-4 w-4 text-green-500" />
                              )}
                              {player.PLAYER}
                            </div>
                          </td>
                          <td className="p-2 text-slate-300">{player.POS}</td>
                          <td className="p-2 text-slate-300">{player.TEAM}</td>
                          <td className="p-2 text-slate-300">{player.GAME}</td>
                          <td className="p-2 text-slate-300">{player.RBI !== '-' ? formatDecimal(parseFloat(player.RBI)) : '-'}</td>
                          <td className="p-2 text-slate-300">{player.R !== '-' ? formatDecimal(parseFloat(player.R)) : '-'}</td>
                          <td className="p-2 text-slate-300">{player.H !== '-' ? formatDecimal(parseFloat(player.H)) : '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Batter Analysis Tab */}
          <TabsContent value="batters">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Batter Hit Analysis</CardTitle>
                <CardDescription className="text-slate-400">
                  Detailed analysis of batter hit opportunities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left p-2 text-slate-300">Player</th>
                        <th className="text-left p-2 text-slate-300">Team</th>
                        <th className="text-left p-2 text-slate-300">Game</th>
                        <th className="text-left p-2 text-slate-300">Projection</th>
                        <th className="text-left p-2 text-slate-300">Line</th>
                        <th className="text-left p-2 text-slate-300">Edge</th>
                        <th className="text-left p-2 text-slate-300">Edge %</th>
                        <th className="text-left p-2 text-slate-300">Confidence</th>
                        <th className="text-left p-2 text-slate-300">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredBatterAnalysis
                        .sort((a, b) => {
                          // First sort by confidence level (recommended bets first)
                          const confidenceOrder = { 'High': 3, 'Medium': 2, 'Low': 1, 'Avoid': 0 }
                          const confidenceDiff = (confidenceOrder[b.CONFIDENCE] || 0) - (confidenceOrder[a.CONFIDENCE] || 0)
                          if (confidenceDiff !== 0) return confidenceDiff
                          
                          // Then sort by edge percentage within same confidence level
                          return b.EDGE_PERCENTAGE - a.EDGE_PERCENTAGE
                        })
                        .map((batter, index) => (
                        <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/25">
                          <td className="p-2 text-white font-medium">{batter.PLAYER}</td>
                          <td className="p-2 text-slate-300">{batter.TEAM}</td>
                          <td className="p-2 text-slate-300">{batter.GAME}</td>
                          <td className="p-2 text-slate-300">{formatDecimal(batter.H_PROJECTION)}</td>
                          <td className="p-2 text-slate-300">{formatDecimal(batter.OPTIMAL_ALT_LINE)}</td>
                          <td className="p-2 text-slate-300">{formatDecimal(batter.EDGE)}</td>
                          <td className="p-2 text-green-400">{formatPercentage(batter.EDGE_PERCENTAGE)}</td>
                          <td className="p-2">
                            <Badge className={getConfidenceBadgeColor(batter.CONFIDENCE)}>
                              {batter.CONFIDENCE}
                            </Badge>
                          </td>
                          <td className="p-2">
                            <Badge className={getRecommendationColor(batter.RECOMMENDATION)}>
                              {batter.RECOMMENDATION}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Pitcher Analysis Tab */}
          <TabsContent value="pitchers">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Pitcher Strikeout Analysis</CardTitle>
                <CardDescription className="text-slate-400">
                  Detailed analysis of pitcher strikeout opportunities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left p-2 text-slate-300">Player</th>
                        <th className="text-left p-2 text-slate-300">Team</th>
                        <th className="text-left p-2 text-slate-300">Game</th>
                        <th className="text-left p-2 text-slate-300">K Projection</th>
                        <th className="text-left p-2 text-slate-300">Line</th>
                        <th className="text-left p-2 text-slate-300">Edge</th>
                        <th className="text-left p-2 text-slate-300">Edge %</th>
                        <th className="text-left p-2 text-slate-300">Confidence</th>
                        <th className="text-left p-2 text-slate-300">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredPitcherAnalysis.map((pitcher, index) => (
                        <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/25">
                          <td className="p-2 text-white font-medium">{pitcher.PLAYER}</td>
                          <td className="p-2 text-slate-300">{pitcher.TEAM}</td>
                          <td className="p-2 text-slate-300">{pitcher.GAME}</td>
                          <td className="p-2 text-slate-300">{formatDecimal(pitcher.K_PROJECTION)}</td>
                          <td className="p-2 text-slate-300">{formatDecimal(pitcher.OPTIMAL_ALT_LINE)}</td>
                          <td className="p-2 text-slate-300">{formatDecimal(pitcher.EDGE)}</td>
                          <td className="p-2 text-green-400">{formatPercentage(pitcher.EDGE_PERCENTAGE)}</td>
                          <td className="p-2">
                            <Badge className={getConfidenceBadgeColor(pitcher.CONFIDENCE)}>
                              {pitcher.CONFIDENCE}
                            </Badge>
                          </td>
                          <td className="p-2">
                            <Badge className={getRecommendationColor(pitcher.RECOMMENDATION)}>
                              {pitcher.RECOMMENDATION}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
