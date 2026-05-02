const { GoogleGenerativeAI } = require('@google/generative-ai');
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function listModels() {
    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyCVT4YZ8LoJQYuSmfRSjVaxGPMsamTaSOg`);
        const data = await response.json();
        console.log("Available models:");
        data.models.forEach(m => console.log(m.name, "-", m.supportedGenerationMethods.join(', ')));
    } catch (error) {
        console.error(error);
    }
}
listModels();
