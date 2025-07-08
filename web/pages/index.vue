<script setup lang="ts">
</script>

<template>
    <section class="py-20 px-4 sm:px-6 lg:px-8">
        <div class="container mx-auto text-center">
            <div class="max-w-4xl mx-auto">
                <h1 class="text-4xl sm:text-6xl font-bold tracking-tight mb-6 text-foreground">
                    AI-Powered Violence Detection
                    <span class="text-primary block">Through Facial Analysis</span>
                </h1>
                <p class="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                    Advanced machine learning technology that analyzes facial expressions and micro-expressions to
                    detect signs of violence and aggression in video content.
                </p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <NuxtLink to="/analyze"
                        class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-11 px-8">
                        Start Analysis
                        <Icon name="lucide:arrow-right" class="ml-2! size-4!" />
                    </NuxtLink>
                    <button
                        class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-11 px-8">
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
                <h2 class="text-3xl font-bold mb-4 text-foreground">Advanced Detection Capabilities</h2>
                <p class="text-muted-foreground max-w-2xl mx-auto">
                    Our AI system uses state-of-the-art computer vision and machine learning to analyze subtle facial
                    cues and expressions.
                </p>
            </div>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="text-center p-6">
                    <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <Icon name="lucide:eye" class="size-6! text-primary!" />
                    </div>
                    <h3 class="text-xl font-semibold mb-2 text-foreground">Facial Expression Analysis</h3>
                    <p class="text-muted-foreground">
                        Detects micro-expressions and emotional states that may indicate aggressive or violent behavior.
                    </p>
                </div>
                <div class="text-center p-6">
                    <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <Icon name="lucide:brain" class="size-6! text-primary!" />
                    </div>
                    <h3 class="text-xl font-semibold mb-2 text-foreground">AI-Powered Insights</h3>
                    <p class="text-muted-foreground">
                        Machine learning models trained on extensive datasets to provide accurate violence detection.
                    </p>
                </div>
                <div class="text-center p-6">
                    <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <Icon name="lucide:zap" class="size-6! text-primary!" />
                    </div>
                    <h3 class="text-xl font-semibold mb-2 text-foreground">Real-time Processing</h3>
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
                <h2 class="text-3xl font-bold mb-4 text-foreground">How It Works</h2>
                <p class="text-muted-foreground max-w-2xl mx-auto">
                    Simple three-step process to analyze your video content for violence detection.
                </p>
            </div>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="text-center">
                    <div
                        class="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 text-primary-foreground font-bold text-xl">
                        1
                    </div>
                    <h3 class="text-xl font-semibold mb-2 text-foreground">Upload Video</h3>
                    <p class="text-muted-foreground">
                        Upload your video file through our secure interface.
                    </p>
                </div>
                <div class="text-center">
                    <div
                        class="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 text-primary-foreground font-bold text-xl">
                        2
                    </div>
                    <h3 class="text-xl font-semibold mb-2 text-foreground">AI Analysis</h3>
                    <p class="text-muted-foreground">
                        Our AI processes facial expressions and behavioral patterns.
                    </p>
                </div>
                <div class="text-center">
                    <div
                        class="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 text-primary-foreground font-bold text-xl">
                        3
                    </div>
                    <h3 class="text-xl font-semibold mb-2 text-foreground">Get Results</h3>
                    <p class="text-muted-foreground">
                        Receive detailed analysis with confidence scores and insights.
                    </p>
                </div>
            </div>
        </div>
    </section>
</template>
