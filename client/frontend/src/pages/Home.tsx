import { useState } from "react"
import { bridge } from "../lib/bridge"


function Home({user}:{user: any}) {

    const [shift, setShift] = useState("Full Day (8 Hours)");
    const [lastAction, setLastAction] = useState("");

    async function handleTimeIn() {
        const result = await bridge.time_in(shift);

        console.log("time in result:", result)

        if (result.ok) {
            const time = new Date(result.time_in).toLocaleTimeString();
            setLastAction(`Time in: ${time}`)
        } else {
            setLastAction(`Error: ${result.error}`)
        }

    }

    async function handleTimeOut() {
        const result = await bridge.time_out();

        if (result.ok) {
            const time = new Date(result.time_out).toLocaleTimeString();
            setLastAction(`Time out: ${time}`)
        } else {
            setLastAction(`Error: ${result.error}`)
        }

    }

  return (
    <main>
        <p>Logged in as {user.email}</p>
        
        <div>
            <select value={shift} onChange={(e) => setShift(e.target.value)}>
                <option value="">Full Day</option>
                <option value="">Half Day</option>
            </select>
        </div>

        <div>
            <button onClick={handleTimeIn}>Time in</button>
            <button onClick={handleTimeOut}>Time out</button>
        </div>

        {lastAction && <p>{lastAction}</p>}

    </main>

)
}

export default Home