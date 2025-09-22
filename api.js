// API Configuration
const API_BASE_URL = 'http://localhost:8000';  // Change this to your server URL when deployed

// API endpoints
const API_ENDPOINTS = {
    health: `${API_BASE_URL}/health`,
    chat: `${API_BASE_URL}/chat`,
    story: `${API_BASE_URL}/story`,
    culture: `${API_BASE_URL}/culture`,
    grammar: `${API_BASE_URL}/grammar`,
    explain: `${API_BASE_URL}/explain`
};

/**
 * Check server health
 */
async function checkServerHealth() {
    try {
        const response = await fetch(API_ENDPOINTS.health, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Server health:', data);
            return data.status === 'healthy';
        }
        return false;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

/**
 * Send message to the Tamil AI assistant
 * @param {string} message - User message
 * @param {string} type - Type of request (generate, story, culture, grammar, explain)
 * @returns {Promise<string>} AI response
 */
async function handleMessage(message, type = 'generate') {
    try {
        // Determine the appropriate endpoint based on type
        let endpoint = API_ENDPOINTS.chat;
        switch (type) {
            case 'story':
                endpoint = API_ENDPOINTS.story;
                break;
            case 'culture':
                endpoint = API_ENDPOINTS.culture;
                break;
            case 'grammar':
                endpoint = API_ENDPOINTS.grammar;
                break;
            case 'explain':
                endpoint = API_ENDPOINTS.explain;
                break;
            default:
                endpoint = API_ENDPOINTS.chat;
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                type: type
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || `Server error: ${response.status}`;
            throw new Error(errorMessage);
        }

        const data = await response.json();
        return data.response;

    } catch (error) {
        console.error('API Error:', error);
        
        // Handle different types of errors
        if (error.message.includes('Failed to fetch')) {
            throw new Error('சேவையகத்துடன் தொடர்பு கொள்ள முடியவில்லை. சேவையகம் இயங்குகிறதா என சரிபார்க்கவும்.');
        } else if (error.message.includes('quota') || error.message.includes('limit')) {
            throw new Error('API வரம்பு முடிந்துவிட்டது. சிறிது நேரம் கழித்து முயற்சிக்கவும்.');
        } else if (error.message.includes('network') || error.message.includes('connection')) {
            throw new Error('இணையதள இணைப்பில் சிக்கல். தயவுசெய்து உங்கள் இணைப்பை சரிபார்க்கவும்.');
        } else {
            throw new Error(error.message || 'எதிர்பாராத பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.');
        }
    }
}

/**
 * Handle specific story requests
 * @param {string} message - User message requesting a story
 * @returns {Promise<string>} Story response
 */
async function requestStory(message) {
    return await handleMessage(message, 'story');
}

/**
 * Handle cultural information requests
 * @param {string} message - User message about Tamil culture
 * @returns {Promise<string>} Cultural information response
 */
async function requestCulturalInfo(message) {
    return await handleMessage(message, 'culture');
}

/**
 * Handle grammar explanations
 * @param {string} message - User message about Tamil grammar
 * @returns {Promise<string>} Grammar explanation response
 */
async function requestGrammarHelp(message) {
    return await handleMessage(message, 'grammar');
}

/**
 * Handle general explanations
 * @param {string} message - User message requesting explanation
 * @returns {Promise<string>} Explanation response
 */
async function requestExplanation(message) {
    return await handleMessage(message, 'explain');
}

/**
 * Detect message type based on content
 * @param {string} message - User message
 * @returns {string} Detected type
 */
function detectMessageType(message) {
    const lowerMessage = message.toLowerCase();
    
    // Story keywords in Tamil, English, and Tanglish
    const storyKeywords = ['கதை', 'story', 'kathai', 'சொல்லு', 'tell me a story', 'ஒரு கதை', 'கேட்க விரும்புகிறேன்'];
    
    // Culture keywords
    const cultureKeywords = ['கலாச்சார', 'culture', 'பண்பாடு', 'பாரம்பரியம', 'tradition', 'festival', 'திருவிழா', 'சடங்கு', 'ritual'];
    
    // Grammar keywords
    const grammarKeywords = ['இலக்கண', 'grammar', 'மொழி', 'language', 'எழுத்து', 'சொல்', 'வாக்கியம', 'sentence', 'தமிழ் கற்க'];
    
    // Explanation keywords
    const explainKeywords = ['விளக்கு', 'explain', 'எப்படி', 'how', 'ஏன்', 'why', 'என்ன', 'what', 'யார்', 'who'];
    
    if (storyKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'story';
    } else if (cultureKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'culture';
    } else if (grammarKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'grammar';
    } else if (explainKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return 'explain';
    }
    
    return 'generate';  // Default type
}

/**
 * Auto-detect and handle message
 * @param {string} message - User message
 * @returns {Promise<string>} AI response
 */
async function autoHandleMessage(message) {
    const detectedType = detectMessageType(message);
    return await handleMessage(message, detectedType);
}

// Error handling utility
function formatErrorMessage(error) {
    if (typeof error === 'string') {
        return error;
    }
    
    if (error.message) {
        return error.message;
    }
    
    return 'எதிர்பாராத பிழை ஏற்பட்டது';
}

// Export functions for use in other scripts (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        checkServerHealth,
        handleMessage,
        requestStory,
        requestCulturalInfo,
        requestGrammarHelp,
        requestExplanation,
        detectMessageType,
        autoHandleMessage,
        formatErrorMessage
    };
}