<script>
export const description
    = 'A sign up form with first name, last name, email and password inside a card. There\'s an option to sign up with GitHub and a link to login if you already have an account'
export const iframeHeight = '600px'
export const containerClass = 'w-full h-screen flex items-center justify-center px-4'
</script>

<script setup>
import { authClient } from "~/lib/auth-client"
const email = ref("");
const password = ref("");

const handleSignUp = async () => {
    const user = {
        email: email.value,
        password: password.value,
    };
    await authClient.signIn.email({
        email: user.email,
        password: user.password,
        callbackURL: "/",
        fetchOptions: {
            onError(context) {
                alert(context.error.message);
            },
            onSuccess() {
                useRouter().push("/");
            },
        },
    });
};
</script>

<template>
    <div class="flex-1 grid place-items-center" @keydown.enter="handleSignUp">
        <Card class="mx-auto w-sm">
            <CardHeader>
                <CardTitle class="text-xl">
                    Sign In
                </CardTitle>
                <CardDescription>
                    Enter your information to log into your account
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="grid gap-4">
                    <div class="grid gap-2">
                        <Label for="email">Email</Label>
                        <Input id="email" type="email" placeholder="m@example.com" required v-model="email" />
                    </div>
                    <div class="grid gap-2">
                        <Label for="password">Password</Label>
                        <Input id="password" type="password" required v-model="password" />
                    </div>
                    <Button type="submit" @click.prevent="handleSignUp" class="w-full">
                        Login
                    </Button>
                </div>
                <div class="mt-4 text-center text-sm">
                    Don't have an account?
                    <NuxtLink to="/sign-up" class="underline">
                        Sign Up
                    </NuxtLink>
                </div>
            </CardContent>
        </Card>
    </div>
</template>