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

  const collections = [];
  
  for (let i = 1; i <= 40; i++) {
    try {
      // FIXED PATH: Changed to ../../../data/
      const hadistData = await import(`../../../data/hadist${i}.json`);
      collections.push({
        id: `hadist${i}`,
        name: hadistData.metadata.collection || `hadist${i}`,
        total_hadist: hadistData.metadata.total_hadist || hadistData.hadist.length,
        endpoint: `/api/hadist/hadist${i}`
      });
    } catch (e) {
      continue;
    }
  }

  return new Response(JSON.stringify({
    message: 'Hadist API Collections',
    total_collections: collections.length,
    collections: collections,
    usage: {
      "get_collection": "/api/hadist/{collection}",
      "get_specific": "/api/hadist/{collection}?no={number}",
      "pagination": "/api/hadist/{collection}?page={page}&limit={limit}",
      "search": "/api/hadist/{collection}?search={keyword}"
    }
  }), {
    headers: corsHeaders
  });
}