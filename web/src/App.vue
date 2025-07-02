<script setup>
import { ref } from 'vue'
import {socket} from './socket.js'

const currentFrame = ref(null)
const frameIdx = ref(0)
const totalFrames = ref(0)
const faceBox = ref([])
const processing = ref(false)
const result = ref(null)
const videoFile = ref(null)
let sessionId = ref(null)

  socket.on('connect', () => {
    sessionId.value = socket.id
    console.log('Socket connected:', sessionId.value)
  })

  socket.on('connected', (data) => {
    console.log('Server confirmed connection:', data.session_id)
  })

  socket.on('frame', (data) => {
    console.log('Received frame:', data)
    frameIdx.value = data.frame_idx
    totalFrames.value = data.total_frames
    faceBox.value = data.face
    currentFrame.value = `data:image/jpeg;base64,${data.frame_img}`
    processing.value = true
  })
  
  socket.on('result', (data) => {
    console.log('Received result:', data)
    processing.value = false
    result.value = data
  })

const uploadVideo = async () => {
  const file = videoFile.value.files[0]
  if (!file) return

  // send session_id so backend can send back events to you
  const formData = new FormData()
  formData.append('video', file)
  formData.append('session_id', sessionId.value)
  processing.value = true
  frameIdx.value = 0
  totalFrames.value = 0
  result.value = null

  await fetch('http://localhost:5000/predict', {
    method: 'POST',
    body: formData,
  })
}
</script>

<template>
  <main>
     <div>
    <form @submit.prevent="uploadVideo">
      <input type="file" ref="videoFile" accept="video/*" required />
      <button type="submit">Upload</button>
    </form>
    <div v-if="processing">
      <p>Processing... Frame {{frameIdx}} / {{totalFrames}}</p>
      <img :src="currentFrame" style="max-width: 400px;" v-if="currentFrame"/>
      <div v-if="faceBox.length">
        <p>Face detected at: [{{faceBox.join(', ')}}]</p>
      </div>
    </div>
    <div v-if="result">
      <h3>Prediction: {{result.prediction}}</h3>
    </div>
  </div>
  </main>
</template>
