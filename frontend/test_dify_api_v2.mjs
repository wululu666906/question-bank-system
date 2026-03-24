import fetch from 'node-fetch'; // Polyfill if needed

const response = await fetch('https://api.dify.ai/v1/workflows/run', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer app-1zVovX8tIiZYR8GoHCzTM7fU',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        inputs: {
            topic: "劳动法辞退",
            question_type: "单选题",
            difficulty: "简单",
            question_count: "1",
            profession: "法务"
        },
        response_mode: 'streaming',
        user: 'system-admin'
    })
});

const reader = response.body;

reader.on('data', (chunk) => {
    console.log(chunk.toString('utf-8'));
});
