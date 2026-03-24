const response = await fetch('https://api.dify.ai/v1/workflows/run', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer app-1zVovX8tIiZYR8GoHCzTM7fU',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        inputs: {
            knowledge_content: "劳动法辞退",
            question_type: "选择题+判断题",
            difficulty_level: "简单",
            question_count: 3,
            job_direction: "法务"
        },
        response_mode: 'streaming',
        user: 'system-admin'
    })
});

console.log("Status:", response.status);
if (!response.ok) {
    console.log("Error Payload:", await response.text());
    process.exit(1);
}

const reader = response.body.getReader();
const decoder = new TextDecoder('utf-8');
let done = false;
while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    if (value) {
        console.log(decoder.decode(value));
    }
}
