import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    // Path to the daily_update.py script (go up from mlb-dashboard to mlb-tool root)
    const scriptPath = path.join(process.cwd(), '..', 'daily_update.py')
    const workingDir = path.join(process.cwd(), '..')
    
    console.log('Running daily update script:', scriptPath)
    console.log('Working directory:', workingDir)
    
    return new Promise((resolve) => {
      const pythonProcess = spawn('python', [scriptPath], {
        cwd: workingDir,
        stdio: ['pipe', 'pipe', 'pipe']
      })
      
      let stdout = ''
      let stderr = ''
      
      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString()
        console.log('Python stdout:', data.toString())
      })
      
      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString()
        console.error('Python stderr:', data.toString())
      })
      
      pythonProcess.on('close', (code) => {
        console.log('Python process exited with code:', code)
        
        if (code === 0) {
          resolve(NextResponse.json({ 
            success: true, 
            message: 'Data update completed successfully',
            output: stdout
          }))
        } else {
          resolve(NextResponse.json({ 
            success: false, 
            message: 'Data update failed',
            error: stderr,
            output: stdout
          }, { status: 500 }))
        }
      })
      
      pythonProcess.on('error', (error) => {
        console.error('Failed to start Python process:', error)
        resolve(NextResponse.json({ 
          success: false, 
          message: 'Failed to start update process',
          error: error.message
        }, { status: 500 }))
      })
    })
    
  } catch (error) {
    console.error('Error in update API:', error)
    return NextResponse.json({ 
      success: false, 
      message: 'Internal server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}