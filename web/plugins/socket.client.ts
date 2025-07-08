// plugins/socket.client.ts
import { io } from 'socket.io-client'

export default defineNuxtPlugin(() => {
  const socket = io('http://localhost:5000') // you can pass options like { path: '/socket.io' }

  return {
    provide: {
      socket
    }
  }
})
