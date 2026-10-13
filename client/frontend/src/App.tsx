import { useState } from "react"
import Login from "./pages/Login";
import Home from "./pages/Home";

function App() {

  const [user, setUser] = useState<any>(null);

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
