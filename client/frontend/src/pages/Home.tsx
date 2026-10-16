import { useState, useEffect } from "react";
import { bridge } from "../lib/bridge";
import { Button } from "../components/ui/button";


function Home({ user }: { user: any }) {
  const [shift, setShift] = useState("Full Day (8 Hours)");
  const [lastAction, setLastAction] = useState("");
  const [todayDtr, setTodayDtr] = useState<any>(null);

  useEffect(() => {
    async function load() {
      const result = await bridge.getDtrToday();
      if (result?.ok && result.dtr) {
        setTodayDtr(result.dtr);
      }
    }
    load().catch((e) => console.error("initial load failed:", e));
  }, []);

  async function handleTimeIn() {
    const result = await bridge.time_in(shift);
    console.log("time in result:", result);

    if (result.ok) {
      const time = new Date(result.time_in).toLocaleTimeString();
      setLastAction(`Time in: ${time}`);
      setTodayDtr((prev: any) => ({
        ...(prev ?? {}),
        time_in: result.time_in,
      }));
    } else {
      setLastAction(`Error: ${result.error}`);
    }
  }

  async function handleTimeOut() {
    const result = await bridge.time_out();

    if (result.ok) {
      const time = new Date(result.time_out).toLocaleTimeString();
      setLastAction(`Time out: ${time}`);
      setTodayDtr((prev: any) => ({
        ...(prev ?? {}),
        time_out: result.time_out,
      }));
    } else {
      setLastAction(`Error: ${result.error}`);
    }
  }

  async function handleLogout() {
    await bridge.logout();
    window.location.reload();
  }

  const timeInDisplay = todayDtr?.time_in
    ? new Date(todayDtr.time_in).toLocaleTimeString()
    : "";

  const timeOutDisplay = todayDtr?.time_out
    ? new Date(todayDtr.time_out).toLocaleTimeString()
    : "";

  return (
    <main>
      <p className="text-2xl">Logged in as {user.email}</p>

      <div>
        <select value={shift} onChange={(e) => setShift(e.target.value)}>
          <option value="Full Day (8 Hours)">Full Day</option>
          <option value="Half Day (4 Hours)">Half Day</option>
        </select>
      </div>

      <div>
        <button onClick={handleTimeIn}>Time in</button>
        <button onClick={handleTimeOut}>Time out</button>
      </div>

      <div className="flex flex-col gap-2">
        <input
          type="text"
          className="bg-white border border-white gap-20"
          value={timeInDisplay}
          disabled
        />
        <input
          type="text"
          className="bg-white border border-white gap-20"
          value={timeOutDisplay}
          disabled
        />
      </div>

      <Button onClick={handleLogout}>
        Log Out
      </Button>

      {lastAction && <p>{lastAction}</p>}
    </main>
  );
}

export default Home;