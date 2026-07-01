import React, {useState, useEffect} from 'react'

const apiBase = process.env.NEXT_PUBLIC_API_URL || ''

function DocList({documents, onSelect}){
  return (
    <div style={{padding:12}}>
      <h3 style={{marginBottom:8}}>Documents</h3>
      <div>
        {documents.length === 0 && <div style={{color:'#666'}}>No documents indexed</div>}
        <ul style={{listStyle:'none', padding:0}}>
          {documents.map(d=> (
            <li key={d.id} style={{marginBottom:8}}>
              <button style={{width:'100%', textAlign:'left'}} onClick={()=>onSelect(d)}>{d.company}</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default function Home(){
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')
  const [results, setResults] = useState([])
  const [documents, setDocuments] = useState([])
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [docChunks, setDocChunks] = useState([])
  const [query, setQuery] = useState('')
  const [token, setToken] = useState(typeof window !== 'undefined' ? localStorage.getItem('token') : null)
  const [authUser, setAuthUser] = useState(null)
  const [authForm, setAuthForm] = useState({username:'', password:''})

  useEffect(()=>{
    fetch(apiBase + '/documents')
      .then(r=>r.json())
      .then(d=>setDocuments(d.documents || []))
      .catch(()=>setDocuments([]))
  },[])

  async function upload(e){
    e.preventDefault()
    if(!file) return
    setStatus('Uploading...')
    const fd = new FormData()
    fd.append('file', file)
    try{
      const headers = token ? { Authorization: `Bearer ${token}` } : {}
      // enqueue job instead of direct processing
      const res = await fetch(apiBase + '/jobs/process', {method:'POST', body: fd, headers})
      if(!res.ok){ setStatus('Enqueue failed'); return }
      const data = await res.json()
      const jobId = data.job_id
      setStatus('Enqueued job '+ jobId)
      // poll job status
      pollJob(jobId)
    }catch(err){
      setStatus('Upload error')
    }
  }

  async function pollJob(jobId){
    setStatus('Processing...')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}
    try{
      const interval = 1500
      const poll = async () => {
        const r = await fetch(apiBase + `/jobs/${jobId}`, {headers})
        if(!r.ok){ setStatus('Job not found'); return }
        const j = await r.json()
        setStatus('Job: '+ j.status)
        if(j.status === 'finished' || j.status === 'failed' || j.status === 'stopped'){
          // refresh documents
          const docs = await fetch(apiBase + '/documents').then(r=>r.json())
          setDocuments(docs.documents || [])
          return
        }
        setTimeout(poll, interval)
      }
      setTimeout(poll, 500)
    }catch(err){ setStatus('Job poll error') }
  }

  async function runSearch(){
    if(!query) return
    setStatus('Searching...')
    try{
      const headers = {'content-type':'application/json'}
      if(token) headers['Authorization'] = `Bearer ${token}`
      const res = await fetch(apiBase + '/search', {method:'POST', headers, body: JSON.stringify({q: query})})
      const data = await res.json()
      setResults(data.results || [])
      setStatus('')
    }catch(err){
      setStatus('Search error')
    }
  }

  async function selectDoc(d){
    setSelectedDoc(d)
    setStatus('Loading chunks...')
    try{
      const headers = token ? { Authorization: `Bearer ${token}` } : {}
      const r = await fetch(apiBase + `/documents/${d.id}/chunks`, {headers})
      const j = await r.json()
      setDocChunks(j.chunks || [])
      setStatus('')
    }catch(err){
      setStatus('Failed to load chunks')
    }
  }

  async function authAction(mode='login'){
    if(!authForm.username || !authForm.password) return setStatus('Enter username & password')
    setStatus(mode === 'login' ? 'Logging in...' : 'Registering...')
    try{
      const res = await fetch(apiBase + (mode === 'login' ? '/auth/login' : '/auth/register'), {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(authForm)})
      const j = await res.json()
      if(j.token){
        localStorage.setItem('token', j.token)
        setToken(j.token)
        setStatus('Authenticated')
      }else{
        setStatus('Auth failed')
      }
    }catch(err){ setStatus('Auth error') }
  }

  return (
    <div style={{fontFamily:'Inter, system-ui, Arial', padding:24, maxWidth:1200, margin:'0 auto'}}>
      <header style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20}}>
        <h1 style={{margin:0}}>AI Due Diligence</h1>
        <div style={{fontSize:14, color:'#666'}}>Enterprise filing analysis</div>
      </header>

      <div style={{display:'grid', gridTemplateColumns:'280px 1fr', gap:20}}>
        <aside style={{background:'#fafafa', border:'1px solid #eee', borderRadius:8}}>
          <DocList documents={documents} onSelect={selectDoc} />
          <div style={{padding:12, borderTop:'1px solid #eee'}}>
            <form onSubmit={upload}>
              <input type='file' accept='application/pdf' onChange={e=>setFile(e.target.files[0])} />
              <div style={{marginTop:8}}>
                <button type='submit'>Upload & Index</button>
              </div>
            </form>
          </div>
        </aside>

        <main>
          <div style={{display:'flex', gap:8, marginBottom:12}}>
            <input value={query} onChange={e=>setQuery(e.target.value)} placeholder='Ask a question about the company...' style={{flex:1, padding:8}} />
            <button onClick={runSearch}>Search</button>
          </div>

          <div style={{display:'flex', gap:8, marginBottom:12}}>
            <input placeholder='username' value={authForm.username} onChange={e=>setAuthForm({...authForm, username:e.target.value})} />
            <input type='password' placeholder='password' value={authForm.password} onChange={e=>setAuthForm({...authForm, password:e.target.value})} />
            <button onClick={()=>authAction('login')}>Login</button>
            <button onClick={()=>authAction('register')}>Register</button>
          </div>

          <section style={{marginBottom:16}}>
            <strong>Status:</strong> {status || 'idle'}
          </section>

          <section style={{marginBottom:20}}>
            <h3>Search Results</h3>
            {results.length === 0 && <div style={{color:'#666'}}>No results</div>}
            {results.map((r,i)=> (
              <div key={i} style={{borderTop:'1px solid #eee', paddingTop:8, marginTop:8}}>
                <div style={{fontSize:12, color:'#888'}}>Score: {typeof r.score === 'number' ? r.score.toFixed(3) : r.score}</div>
                <div style={{fontWeight:600}}>{r.chunk.section} — pages {r.chunk.start_page}-{r.chunk.end_page}</div>
                <div style={{marginTop:6}}>{r.chunk.text.substring(0,400)}...</div>
              </div>
            ))}
          </section>

          <section>
            <h3>Chunks for {selectedDoc ? selectedDoc.company : '...'}</h3>
            {docChunks.length === 0 && <div style={{color:'#666'}}>No chunks loaded</div>}
            {docChunks.map((c,i)=> (
              <div key={i} style={{borderTop:'1px solid #eee', paddingTop:8, marginTop:8}}>
                <div style={{fontWeight:600}}>{c.section} — pages {c.start_page}-{c.end_page}</div>
                <div style={{marginTop:6}}>{c.text.substring(0,400)}...</div>
              </div>
            ))}
          </section>
        </main>
      </div>
    </div>
  )
}
