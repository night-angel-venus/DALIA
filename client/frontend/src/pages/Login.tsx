import React from 'react'
import { useState, useEffect } from 'react'
import { bridge } from '../lib/bridge';

import { Button } from '../components/ui/button';

function Login({onSuccess}:{onSuccess:  (user:any) => void}) {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [ready, setReady] = useState(false);


    useEffect(() => {
       const check = setInterval(()=>{
        if (bridge.ready()) {
            setReady(true);
            clearInterval(check);
        }
       }, 50);
       return () => clearInterval(check) 
    }, []);


    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError("")

        const result = await bridge.login(email, password);

        if (result.ok) {
            onSuccess(result.user);
        } else {
            setError(result.error ?? "Login failed");
        }
    }


  return (
    <main>
        <h1>LOGIN</h1>

        <form onSubmit={handleSubmit}>
            <input 
            type="email"
            value={email}
            placeholder='Enter email' 
            onChange={(e)=>setEmail(e.target.value)}/>
            <input 
            type="password"
            value={password}
            placeholder='Enter Password' 
            onChange={(e) => setPassword(e.target.value)}/>
            
            {error && <p>{error}</p>}
        
            <Button type="submit">
                {ready ? "Log in":"Logging you in..."}
            </Button>


        </form>      
    </main>
)
}

export default Login