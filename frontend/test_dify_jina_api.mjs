const response = await fetch('https://api.dify.ai/v1/workflows/run', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer app-1zVovX8tIiZYR8GoHCzTM7fU',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        inputs: {
            topic: "劳动法辞退",
            question_type: "简答题",
            difficulty: "中等",
            question_count: "2",
            profession: "法务"
        },
        response_mode: 'streaming',
        user: 'system-admin'
    })
});

console.log("Status:", response.status);

const reader = response.body.getReader();
const decoder = new TextDecoder('utf-8');
let done = false;
while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    if (value) {
        const text = decoder.decode(value);
        console.log(text);
    }
}
