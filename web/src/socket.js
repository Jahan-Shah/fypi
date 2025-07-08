import { io } from "socket.io-client";

// "undefined" means the URL will be computed from the `window.location` object
const URL = "https://3ee5-103-104-87-32.ngrok-free.app";

export const socket = io(URL);
