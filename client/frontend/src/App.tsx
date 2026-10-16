import { useState, useEffect } from "react"
import Login from "./pages/Login";
import Home from "./pages/Home";
import { bridge } from "./lib/bridge";

function App() {

  const [user, setUser] = useState<any>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function check() {
      const currentUser = await bridge.getCurrentUser();

      if (currentUser) {
        setUser(currentUser)
      }
      setChecking(false)
    }

    const waitPyWebView = setInterval(()=>{
      if (bridge.ready()) {
        clearInterval(waitPyWebView);
        check()
      }
    }, 50)

    return ()=> clearInterval(waitPyWebView)
  }, []);

  if (checking) {
    return <div>Loading...</div>
  }

  if (!user) {
    return <Login onSuccess = {setUser}/>
  }

  return (
    <>
      <Home user={user}/>
    </>
  )
}

export default App
