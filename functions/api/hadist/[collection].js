// functions/api/hadist/[collection].js
export async function onRequest(context) {
  const { request, env, params } = context;
  const { collection } = params;
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  if (request.method !== 'GET') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    const hadistData = await import(`../../../data/${collection}.json`);
    
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page')) || 1;
    const limit = parseInt(url.searchParams.get('limit')) || 10;
    const search = url.searchParams.get('search') || '';
    const no = url.searchParams.get('no');

    let hadist = hadistData.hadist;
    
    if (no) {
      const hadistNo = parseInt(no);
      const foundHadist = hadist.find(h => h.no === hadistNo);
      
      if (!foundHadist) {
        return new Response(JSON.stringify({ 
          error: 'Hadist not found',
          collection: collection
        }), {
          status: 404,
          headers: corsHeaders
        });
      }
      
      return new Response(JSON.stringify({
        metadata: hadistData.metadata,
        collection: collection,
        hadist: foundHadist
      }), {
        headers: corsHeaders
      });
    }

    if (search) {
      hadist = hadist.filter(h => 
        h.arab.toLowerCase().includes(search.toLowerCase()) ||
        h.indo.toLowerCase().includes(search.toLowerCase())
      );
    }

    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedHadist = hadist.slice(startIndex, endIndex);

    const response = {
      metadata: {
        ...hadistData.metadata,
        collection: collection,
        current_page: page,
        per_page: limit,
        total_pages: Math.ceil(hadist.length / limit),
        total_filtered: hadist.length
      },
      hadist: paginatedHadist
    };

    return new Response(JSON.stringify(response), {
      headers: corsHeaders
    });

  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'Collection not found',
      collection: collection
    }), {
      status: 404,
      headers: corsHeaders
    });
  }
}