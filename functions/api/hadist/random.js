// functions/api/random.js
export async function onRequest(context) {
  const { request } = context;
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const randomFileNum = Math.floor(Math.random() * 40) + 1;
    const hadistData = await import(`../../data/hadist${randomFileNum}.json`);
    
    const randomIndex = Math.floor(Math.random() * hadistData.hadist.length);
    const randomHadist = hadistData.hadist[randomIndex];

    return new Response(JSON.stringify({
      metadata: hadistData.metadata,
      collection: `hadist${randomFileNum}`,
      hadist: randomHadist
    }), {
      headers: corsHeaders
    });

  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'Internal server error'
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}