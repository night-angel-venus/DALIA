import { useState } from "react"
import Login from "./pages/Login";

function App() {

  const [user, setUser] = useState<any>(null);

  if (!user) {
    return <Login onSuccess = {setUser}/>
  }

  return (
    <>
      <p>Hello, {user.email}</p>
    </>
  )
}

export default App
