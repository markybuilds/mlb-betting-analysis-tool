import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), '..', 'analysis', 'batter_hits_analysis.json')
    const fileContents = fs.readFileSync(filePath, 'utf8')
    const data = JSON.parse(fileContents)
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error reading batter analysis file:', error)
    return NextResponse.json({ error: 'Failed to load batter analysis data' }, { status: 500 })
  }
}