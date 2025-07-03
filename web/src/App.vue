<script setup>
import { ref } from 'vue'
import { 
  Shield, Menu, ArrowRight, Eye, Brain, Zap, Upload, FileVideo, 
  X, Play, Loader2,
} from 'lucide-vue-next'
import { socket } from './socket'

// Reactive data
const currentView = ref('home')
const mobileMenuOpen = ref(false)
const selectedFile = ref(null)
const isDragging = ref(false)
const isAnalyzing = ref(false)
const analysisResult = ref(null)
const currentFrame = ref(null)
const frameIdx = ref(0)
const totalFrames = ref(0)
const faceBox = ref([])
const processing = ref(false)
const result = ref(null)
const sessionId = ref(null)

  socket.on('connect', () => {
    sessionId.value = socket.id
    console.log('Socket connected:', sessionId.value)
  })

  socket.on('connected', (data) => {
    console.log('Server confirmed connection:', data.session_id)
  })

  socket.on('frame', (data) => {
    console.log('Received frame:', data)
    isAnalyzing.value = true
    frameIdx.value = data.frame_idx
    totalFrames.value = data.total_frames
    faceBox.value = data.face
    currentFrame.value = `data:image/jpeg;base64,${data.frame_img}`
    processing.value = true
  })
  
  socket.on('result', (data) => {
    console.log('Received result:', data)
    isAnalyzing.value = false
    processing.value = false
    result.value = data
  })

// File handling
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('video/')) {
    selectedFile.value = file
  }
}

const removeFile = () => {
  selectedFile.value = null
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Analysis functions
const analyzeVideo = async () => {
  if (!selectedFile.value) return
  try {
    const formData = new FormData()
    formData.append('video', selectedFile.value)
    await fetch('/api/predict', {
      method: 'POST',
      body: formData
    })
    
  } catch (error) {
    console.error('Analysis failed:', error)
  }
}

// const getScoreColor = (score) => {
//   if (score >= 70) return 'bg-red-100 text-red-800 border border-red-200'
//   if (score >= 40) return 'bg-yellow-100 text-yellow-800 border border-yellow-200'
//   return 'bg-green-100 text-green-800 border border-green-200'
// }

// const getScoreDescription = (score) => {
//   if (score >= 70) return 'High probability of violence detected'
//   if (score >= 40) return 'Moderate violence indicators present'
//   return 'Low violence probability - content appears safe'
// }
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Navigation -->
    <nav class="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-2">
            <Shield class="h-8 w-8 text-primary" />
            <span class="text-xl font-bold">Vision Guard</span>
          </div>
          <div class="hidden md:flex space-x-8">
            <button 
              @click="currentView = 'home'" 
              :class="currentView === 'home' ? 'text-primary' : 'text-muted-foreground hover:text-foreground'"
              class="transition-colors"
            >
              Home
            </button>
            <button 
              @click="currentView = 'app'" 
              :class="currentView === 'app' ? 'text-primary' : 'text-muted-foreground hover:text-foreground'"
              class="transition-colors"
            >
              Analyze Video
            </button>
          </div>
          <div class="md:hidden">
            <button @click="mobileMenuOpen = !mobileMenuOpen" class="p-2">
              <Menu class="h-6 w-6" />
            </button>
          </div>
        </div>
        <!-- Mobile menu -->
        <div v-if="mobileMenuOpen" class="md:hidden py-4 space-y-2">
          <button 
            @click="currentView = 'home'; mobileMenuOpen = false" 
            class="block w-full text-left px-2 py-1 text-muted-foreground hover:text-foreground"
          >
            Home
          </button>
          <button 
            @click="currentView = 'app'; mobileMenuOpen = false" 
            class="block w-full text-left px-2 py-1 text-muted-foreground hover:text-foreground"
          >
            Analyze Video
          </button>
        </div>
      </div>
    </nav>

    <!-- Home Page -->
    <div v-if="currentView === 'home'">
      <!-- Hero Section -->
      <section class="py-20 px-4 sm:px-6 lg:px-8">
        <div class="container mx-auto text-center">
          <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl sm:text-6xl font-bold tracking-tight mb-6">
              AI-Powered Violence Detection
              <span class="text-primary block">Through Facial Analysis</span>
            </h1>
            <p class="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Advanced machine learning technology that analyzes facial expressions and micro-expressions to detect signs of violence and aggression in video content.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                @click="currentView = 'app'"
                class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-11 px-8"
              >
                Start Analysis
                <ArrowRight class="ml-2 h-4 w-4" />
              </button>
              <button class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-11 px-8">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
        <div class="container mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold mb-4">Advanced Detection Capabilities</h2>
            <p class="text-muted-foreground max-w-2xl mx-auto">
              Our AI system uses state-of-the-art computer vision and machine learning to analyze subtle facial cues and expressions.
            </p>
          </div>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="text-center p-6">
              <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Eye class="h-6 w-6 text-primary" />
              </div>
              <h3 class="text-xl font-semibold mb-2">Facial Expression Analysis</h3>
              <p class="text-muted-foreground">
                Detects micro-expressions and emotional states that may indicate aggressive or violent behavior.
              </p>
            </div>
            <div class="text-center p-6">
              <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Brain class="h-6 w-6 text-primary" />
              </div>
              <h3 class="text-xl font-semibold mb-2">AI-Powered Insights</h3>
              <p class="text-muted-foreground">
                Machine learning models trained on extensive datasets to provide accurate violence detection.
              </p>
            </div>
            <div class="text-center p-6">
              <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap class="h-6 w-6 text-primary" />
              </div>
              <h3 class="text-xl font-semibold mb-2">Real-time Processing</h3>
              <p class="text-muted-foreground">
                Fast analysis and results delivery for immediate actionable insights.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- How It Works Section -->
      <section class="py-20 px-4 sm:px-6 lg:px-8">
        <div class="container mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold mb-4">How It Works</h2>
            <p class="text-muted-foreground max-w-2xl mx-auto">
              Simple three-step process to analyze your video content for violence detection.
            </p>
          </div>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="text-center">
              <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 text-primary-foreground font-bold text-xl">
                1
              </div>
              <h3 class="text-xl font-semibold mb-2">Upload Video</h3>
              <p class="text-muted-foreground">
                Upload your video file through our secure interface.
              </p>
            </div>
            <div class="text-center">
              <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 text-primary-foreground font-bold text-xl">
                2
              </div>
              <h3 class="text-xl font-semibold mb-2">AI Analysis</h3>
              <p class="text-muted-foreground">
                Our AI processes facial expressions and behavioral patterns.
              </p>
            </div>
            <div class="text-center">
              <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 text-primary-foreground font-bold text-xl">
                3
              </div>
              <h3 class="text-xl font-semibold mb-2">Get Results</h3>
              <p class="text-muted-foreground">
                Receive detailed analysis with confidence scores and insights.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- App Page -->
    <div v-if="currentView === 'app'" class="py-8 px-4 sm:px-6 lg:px-8">
      <div class="container mx-auto max-w-4xl">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold mb-2">Video Violence Detection</h1>
          <p class="text-muted-foreground">
            Upload a video file to analyze for signs of violence through facial expression detection.
          </p>
        </div>

        <!-- Upload Section -->
        <div class="rounded-lg border bg-card text-card-foreground shadow-sm mb-8">
          <div class="p-6">
            <h3 class="text-lg font-semibold mb-4">Upload Video</h3>
            <div 
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent
              :class="isDragging ? 'border-primary bg-primary/5' : 'border-dashed border-muted-foreground/25'"
              class="border-2 rounded-lg p-8 text-center transition-colors cursor-pointer"
              @click="$refs.fileInput.click()"
            >
              <input 
                ref="fileInput"
                type="file" 
                accept="video/*" 
                @change="handleFileSelect"
                class="hidden"
              >
              <Upload class="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p class="text-lg font-medium mb-2">
                {{ selectedFile ? selectedFile.name : 'Drop your video here or click to browse' }}
              </p>
              <p class="text-sm text-muted-foreground">
                Supports MP4, AVI, MOV files up to 100MB
              </p>
            </div>
            
            <div v-if="selectedFile" class="mt-4 flex items-center justify-between p-4 bg-muted rounded-lg">
              <div class="flex items-center space-x-3">
                <FileVideo class="h-5 w-5 text-primary" />
                <div>
                  <p class="font-medium">{{ selectedFile.name }}</p>
                  <p class="text-sm text-muted-foreground">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
              </div>
              <button 
                @click="removeFile"
                class="text-muted-foreground hover:text-foreground"
              >
                <X class="h-5 w-5" />
              </button>
            </div>

            <button 
              @click="analyzeVideo"
              :disabled="!selectedFile || isAnalyzing"
              class="w-full mt-4 inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-11 px-8"
            >
              <span v-if="isAnalyzing" class="flex items-center">
                <Loader2 class="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </span>
              <span v-else class="flex items-center">
                <Play class="mr-2 h-4 w-4" />
                Start Analysis
              </span>
            </button>
          </div>
        </div>

        <!-- Progress Section -->
        <div v-if="isAnalyzing" class="rounded-lg border bg-card text-card-foreground shadow-sm mb-8">
          <div class="p-6">
            <h3 class="text-lg font-semibold mb-4">Analysis Progress</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">Processing... Frame {{frameIdx}} / {{totalFrames}}</span>
                <img :src="currentFrame" 
                alt="Current Frame" 
                class="w-32 h-32 object-cover rounded-lg border border-muted-foreground"
                v-if="currentFrame" />
              </div>
              <span v-if="result" class="text-sm font-medium">Prediction: {{result.prediction}}</span>
              <span v-if="result" class="text-sm font-medium">violent%: {{result.violent}}</span>
              <span v-if="result" class="text-sm font-medium">non-violent%: {{result.nonViolent}}</span>
            </div>
          </div>
        </div>

        <!-- Results Section -->
        <div v-if="analysisResult" class="rounded-lg border bg-card text-card-foreground shadow-sm">
          <!-- <div class="p-6">
            <h3 class="text-lg font-semibold mb-4">Analysis Results</h3>
            
            <div class="mb-6 p-4 rounded-lg" :class="getScoreColor(analysisResult.violenceScore)">
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium">Violence Detection Score</span>
                <span class="text-2xl font-bold">{{ analysisResult.violenceScore }}%</span>
              </div>
              <div class="text-sm opacity-90">
                {{ getScoreDescription(analysisResult.violenceScore) }}
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-6">
              <div>
                <h4 class="font-medium mb-3">Facial Expression Analysis</h4>
                <div class="space-y-2">
                  <div v-for="expression in analysisResult.expressions" :key="expression.type" class="flex justify-between">
                    <span class="text-sm">{{ expression.type }}</span>
                    <span class="text-sm font-medium">{{ expression.confidence }}%</span>
                  </div>
                </div>
              </div>
              <div>
                <h4 class="font-medium mb-3">Detection Metrics</h4>
                <div class="space-y-2">
                  <div class="flex justify-between">
                    <span class="text-sm">Faces Detected</span>
                    <span class="text-sm font-medium">{{ analysisResult.facesDetected }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm">Processing Time</span>
                    <span class="text-sm font-medium">{{ analysisResult.processingTime }}s</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm">Confidence Level</span>
                    <span class="text-sm font-medium">{{ analysisResult.confidence }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-6">
              <h4 class="font-medium mb-3">Violence Detection Timeline</h4>
              <div class="space-y-2">
                <div v-for="event in analysisResult.timeline" :key="event.timestamp" class="flex items-center space-x-3 p-2 rounded bg-muted/50">
                  <div class="w-2 h-2 rounded-full" :class="event.severity === 'high' ? 'bg-red-500' : event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'"></div>
                  <span class="text-sm font-medium">{{ event.timestamp }}s</span>
                  <span class="text-sm">{{ event.description }}</span>
                  <span class="text-sm text-muted-foreground ml-auto">{{ event.confidence }}%</span>
                </div>
              </div>
            </div>
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>
