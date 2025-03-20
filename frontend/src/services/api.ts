
const API_BASE_URL = 'http://localhost:8000';


export const LLMChatProccess= async(message: string) => {

    try{
        const response = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
            },
            body: JSON.stringify({
                message, 
                chatHistory: []
                
            }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error in editSubTask:', error);
        throw error;
    }





}