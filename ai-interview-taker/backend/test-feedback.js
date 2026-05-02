const { GoogleGenerativeAI } = require('@google/generative-ai');
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function testFeedback() {
    try {
        const model = genAI.getGenerativeModel({ model: "gemini-2.5-pro" });
        const result = await model.generateContent("Say hello world");
        console.log(result.response.text());
    } catch (e) {
        console.error("Error:", e);
    }
}
testFeedback();
