import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

export function formatDecimal(value: number): string {
  return value.toFixed(2)
}

export function getConfidenceBadgeColor(confidence: string): string {
  switch (confidence.toLowerCase()) {
    case 'high':
      return 'bg-green-100 text-green-800 border-green-200'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    case 'low':
      return 'bg-red-100 text-red-800 border-red-200'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200'
  }
}

export function getRecommendationColor(recommendation: string): string {
  if (recommendation.toLowerCase().includes('over')) {
    return 'bg-blue-100 text-blue-800 border-blue-200'
  } else if (recommendation.toLowerCase().includes('under')) {
    return 'bg-purple-100 text-purple-800 border-purple-200'
  }
  return 'bg-gray-100 text-gray-800 border-gray-200'
}