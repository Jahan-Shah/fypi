import { io } from "socket.io-client";

// "undefined" means the URL will be computed from the `window.location` object
const URL = "https://8f56-103-104-87-47.ngrok-free.app";

export const socket = io(URL);
