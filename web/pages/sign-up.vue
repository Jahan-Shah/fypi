<script>
export const description
    = 'A sign up form with first name, last name, email and password inside a card. There\'s an option to sign up with GitHub and a link to login if you already have an account'
export const iframeHeight = '600px'
export const containerClass = 'w-full h-screen flex items-center justify-center px-4'
</script>

<script setup>
import { authClient } from "~/lib/auth-client"
const firstName = ref("");
const lastName = ref("");
const email = ref("");
const password = ref("");

const handleSignUp = async () => {
    const user = {
        firstName: firstName.value,
        lastName: lastName.value,
        email: email.value,
        password: password.value,
    };
    await authClient.signUp.email({
        email: user.email,
        password: user.password,
        name: `${user.firstName} ${user.lastName}`,
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
        <Card class="mx-auto max-w-sm">
            <CardHeader>
                <CardTitle class="text-xl">
                    Sign Up
                </CardTitle>
                <CardDescription>
                    Enter your information to create an account
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="grid gap-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="grid gap-2">
                            <Label for="first-name">First name</Label>
                            <Input id="first-name" placeholder="Max" required v-model="firstName"/>
                        </div>
                        <div class="grid gap-2">
                            <Label for="last-name">Last name</Label>
                            <Input id="last-name" placeholder="Robinson" required v-model="lastName"/>
                        </div>
                    </div>
                    <div class="grid gap-2">
                        <Label for="email">Email</Label>
                        <Input id="email" type="email" placeholder="m@example.com" required v-model="email" />
                    </div>
                    <div class="grid gap-2">
                        <Label for="password">Password</Label>
                        <Input id="password" type="password" required v-model="password" />
                    </div>
                    <Button type="submit" @click.prevent="handleSignUp"   class="w-full">
                        Create an account
                    </Button>
                </div>
                <div class="mt-4 text-center text-sm">
                    Already have an account?
                    <NuxtLink to="/sign-in" class="underline">
                        Sign in
                    </NuxtLink>
                </div>
            </CardContent>
        </Card>
    </div>
</template>