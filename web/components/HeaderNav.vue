<script setup>
import { authClient } from "~/lib/auth-client";

const { data: session } = await authClient.useSession(useFetch);
const mobileMenuOpen = ref(false)
</script>

<template>
    <nav class="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center space-x-2">
                    <Icon name="lucide:shield" class="size-8! text-primary!" />
                    <span class="text-xl font-bold">Vision Guard</span>
                </div>
                <div class="hidden md:flex space-x-8">
                    <NuxtLink to="/"
                        class="p-2 rounded transition-colors text-muted-foreground hover:text-foreground focus:outline-none"
                        active-class="text-primary border-b-2 border-primary">Home</NuxtLink>
                    <NuxtLink to="/analyze"
                        class="p-2 rounded transition-colors text-muted-foreground hover:text-foreground focus:outline-none"
                        active-class="text-primary border-b-2 border-primary">Analyze Video</NuxtLink>
                    <Button v-if="session" variant="outline" @click="async () => {
                        await authClient.signOut()
                        useRouter().push('/sign-in')
                    }">
                        <Icon name="lucide:log-out" />
                    </Button>
                </div>
                <div class="md:hidden">
                    <button @click="mobileMenuOpen = !mobileMenuOpen" class="p-2">
                        <Icon name="lucide:menu" class="size-6!" />
                    </button>
                </div>
            </div>
            <!-- Mobile menu -->
            <div v-if="mobileMenuOpen" class="md:hidden py-4 space-y-2">
                <NuxtLink to="/home" class="transition-colors text-muted-foreground hover:text-foreground p-2 rounded"
                    activeClass="text-primary border">Home</NuxtLink>
                <NuxtLink to="/analyze"
                    class="transition-colors text-muted-foreground hover:text-foreground p-2 rounded"
                    activeClass="text-primary border">Analyze Video</NuxtLink>
            </div>
        </div>
    </nav>
</template>