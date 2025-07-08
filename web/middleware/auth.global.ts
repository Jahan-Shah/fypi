import { authClient } from "~/lib/auth-client";
export default defineNuxtRouteMiddleware(async (to, from) => {
    const { data: session } = await authClient.useSession(useFetch);
    if (!session.value) {
        if (to.path === "/" || to.path === '/analyze') {
            return navigateTo("/sign-in");
        }
    }
    if (session.value) {
        if (to.path === "/sign-up" || to.path === '/sign-in') {
            return navigateTo("/");
        }
    }
});