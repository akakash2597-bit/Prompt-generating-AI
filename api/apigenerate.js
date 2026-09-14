// api/generate.js
// Runs on Vercel's server, NOT in the browser — this is the only safe place
// to use your Gemini API key. The frontend calls THIS endpoint,
// never generativelanguage.googleapis.com directly.

export default async function handler(req, res) {
  // Basic CORS so your frontend (same domain, but harmless to include) can call this
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { systemPrompt, userPrompt } = req.body || {};

  if (!systemPrompt || !userPrompt) {
    return res.status(400).json({ error: 'Missing systemPrompt or userPrompt' });
  }

  if (!process.env.GEMINI_API_KEY) {
    return res.status(500).json({ error: 'Server is missing GEMINI_API_KEY — set it in Vercel project settings and redeploy.' });
  }

  const GEMINI_MODEL = 'gemini-2.5-flash'; // fast + cheap; swap to gemini-2.5-pro for higher quality
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': process.env.GEMINI_API_KEY
      },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemPrompt }] },
        contents: [{ role: 'user', parts: [{ text: userPrompt }] }],
        generationConfig: {
          responseMimeType: 'application/json',
          maxOutputTokens: 1000
        }
      })
    });

    const data = await response.json();

    if (!response.ok) {
      // Surface Gemini's own error message (bad key, quota, etc.) to the frontend
      return res.status(response.status).json({ error: data?.error?.message || 'Gemini API error' });
    }

    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}