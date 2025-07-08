<script setup>
const selectedFile = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const isAnalyzing = ref(false)
const processing = ref(false)
const result = ref(null)
const sessionId = ref(null)
const currentFrame = ref(null)
const frameIdx = ref(0)
const totalFrames = ref(0)
const faceBox = ref([])

const { $socket } = useNuxtApp()

onMounted(() => {
    $socket.on('connect', () => {
        sessionId.value = $socket.id
        console.log('$Socket connected:', sessionId.value)
    })

    $socket.on('connected', (data) => {
        console.log('Server confirmed connection:', data.session_id)
    })

    $socket.on('frame', (data) => {
        isAnalyzing.value = true
        frameIdx.value = data.frame_idx
        totalFrames.value = data.total_frames
        faceBox.value = data.face
        currentFrame.value = `data:image/jpeg;base64,${data.frame_img}`
        processing.value = true
    })

    $socket.on('result', (data) => {
        console.log('Received result:', data)
        isAnalyzing.value = false
        // processing.value = false
        result.value = data
    })
})

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

async function analyzeVideo() {
    result.value = null
    if (!selectedFile.value) return

    isUploading.value = true

    try {
        const formData = new FormData()
        formData.append('video', selectedFile.value)
        formData.append('session_id', sessionId.value)

        const response = await $fetch('/api2/predict', {
            method: 'POST',
            body: formData,
        })
    } catch (error) {
        console.error('Analysis failed:', error)
    } finally {
        isUploading.value = false
    }
}

</script>

<template>
    <div class="py-8 px-4 sm:px-6 lg:px-8">
        <div class="container mx-auto max-w-4xl">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold mb-2">Video Violence Detection</h1>
                <p class="text-muted-foreground">
                    Upload a video file to analyze for signs of violence through facial expression detection.
                </p>
            </div>
            <div class="rounded-lg border bg-card text-card-foreground shadow-sm mb-8">
                <div class="p-6">
                    <h3 class="text-lg font-semibold mb-4">Upload Video</h3>
                    <div @drop="handleDrop" @dragover.prevent @dragenter.prevent
                        :class="isDragging ? 'border-primary bg-primary/5' : 'border-dashed border-muted-foreground/25'"
                        class="border-2 rounded-lg p-8 text-center transition-colors cursor-pointer"
                        @click="$refs.fileInput.click()">
                        <input ref="fileInput" type="file" accept="video/*" @change="handleFileSelect" class="hidden">
                        <Icon name="lucide:upload" class="size-12! mx-auto! mb-4! text-muted-foreground!" />
                        <p class="text-lg font-medium mb-2">
                            {{ selectedFile ? selectedFile.name : 'Drop your video here or click to browse' }}
                        </p>
                        <p class="text-sm text-muted-foreground">
                            Supports MP4, AVI, MOV files up to 100MB
                        </p>
                    </div>

                    <div v-if="selectedFile" class="mt-4 flex items-center justify-between p-4 bg-muted rounded-lg">
                        <div class="flex items-center space-x-3">
                            <Icon name="lucide:file-video" class="size-5! text-primary!" />
                            <div>
                                <p class="font-medium">{{ selectedFile.name }}</p>
                                <p class="text-sm text-muted-foreground">{{ formatFileSize(selectedFile.size) }}</p>
                            </div>
                        </div>
                        <button @click="removeFile" class="text-muted-foreground hover:text-foreground">
                            <Icon name="lucide:x" class="size-5! text-!" />
                        </button>
                    </div>

                    <ClientOnly>
                        <button @click="analyzeVideo" :disabled="!selectedFile || isAnalyzing || isUploading"
                        class="w-full mt-4 inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-11 px-8">
                        <span v-if="isUploading" class="flex items-center">
                            <Icon name="lucide:loader-2" class="size-4! mr-2! animate-spin!" />
                            Uploading...
                        </span>
                        <span v-else-if="isAnalyzing" class="flex items-center">
                            <Icon name="lucide:loader-2" class="size-4! mr-2! animate-spin!" />
                            Analyzing...
                        </span>
                        <span v-else class="flex items-center">
                            <Icon name="lucide:play" class="size-4! mr-2!" />
                            Start Analysis
                        </span>
                    </button>
                </ClientOnly>
                </div>
            </div>
            <div v-if="processing" class="rounded-lg border bg-card text-card-foreground shadow-sm mb-8">
                <div class="p-6">
                    <h3 class="text-lg font-semibold mb-4">Analysis Progress</h3>
                    <div class="space-y-4">
                        <div class="flex flex-col items-center justify-between">
                            <span class="text-sm font-medium">Processing... Frame {{ frameIdx }} / {{ totalFrames
                                }}</span>
                            <img :src="currentFrame" alt="Current Frame"
                                class="w-full object-contain border border-muted-foreground" v-if="currentFrame" />
                        </div>
                        <div v-if="result" class="space-x-4">
                            <span class="text-sm font-medium">Prediction: {{ result.prediction }}</span>
                            <span class="text-sm font-medium">violent%: {{ Number(result.violent).toFixed(2) }}</span>
                            <span class="text-sm font-medium">non-violent%: {{
                                Number(result.nonViolent).toFixed(2) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>