import { useState, useEffect } from "react";
import { bridge } from "../lib/bridge";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card"
import { Label } from "../components/ui/label";


function Home({ user }: { user: any }) {
  const [shift, setShift] = useState("");
  const [todayDtr, setTodayDtr] = useState<any>(null);
  const [currentTime, setCurrentTime] = useState('');


  useEffect(() => {
    const updateTime = () => {
      const timeString = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', hour12: false
      });
      setCurrentTime(timeString);
    }

    updateTime()

    const timerId = setInterval(updateTime, 1000);

    return () => clearInterval(timerId)
  }, []);

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
      setTodayDtr((prev: any) => ({
        ...(prev ?? {}),
        time_in: result.time_in,
      }));
    } else {
    }
  }

  async function handleTimeOut() {
    const result = await bridge.time_out();

    if (result.ok) {
      setTodayDtr((prev: any) => ({
        ...(prev ?? {}),
        time_out: result.time_out,
      }));
    } else {
    }
  }

  async function handleLogout() {
    await bridge.logout();
    window.location.reload();
  }

  const timeInDisplay = todayDtr?.time_in
    ? new Date(todayDtr.time_in).toLocaleTimeString('en-US', {
      hour: '2-digit', minute: '2-digit', hour12:false
    })
    : "";

  const timeOutDisplay = todayDtr?.time_out
    ? new Date(todayDtr.time_out).toLocaleTimeString('en-US', {
      hour: '2-digit', minute: '2-digit', hour12:false
    })
    : "";



  const dateToday = new Date().toLocaleDateString('en-US', {
    month: 'long', day: 'numeric', year: 'numeric'
  });

  // const currentTime = new Date().toLocaleTimeString('en-US', {
  //   hour: '2-digit', minute:'2-digit', second: '2-digit',hour12: false
  // })

  return (
    <main className="px-12 py-7 w-screen h-screen border flex flex-col justify-center gap-6 bg-[#9a0002]">
      {/* <p className="text-2xl">Logged in as {user.email}</p> */}

      <Card className="bg-[#efe6dd] p-2 py-6 flex flex-col h-70 gap-3">

        <CardHeader>
          <div className="py-4 text-center text-[18px] border border-black rounded-lg font-bold text-[#9a0002]
          border border-white/60 bg-[#efe6dd]/30 backdrop-blur-md 
          shadow-[inset_0_4px_12px_rgba(0,0,0,0.15),inset_0_2px_4px_rgba(0,0,0,0.1)]
          
          ">
            Hello, {user.username}!
          </div>
        </CardHeader>
        <CardContent className="w-full flex flex-col gap-2 ">
          <Label className="text-[#9a0002]">Shift Type</Label>
          <div className="grid grid-cols-2 gap-3">
            <Button className="cursor-pointer h-5 py-3 rounded-sm text-[10px] text-[#9a0002] bg-[#e5b85c]" value="Full Day (8 Hours)" onClick={() => setShift("Full Day (8 Hours)")} disabled={shift === "Half Day (4 Hours)"}>Full Day (8 Hours)</Button>
            <Button className="cursor-pointer h-5 py-3 rounded-sm w-full text-[10px] text-[#9a0002] bg-[#e5b85c]" value="Half Day (4 Hours)" onClick={() => setShift("Half Day (4 Hours)")} disabled={shift === "Full Day (8 Hours)"}>Half Day (4 Hours)</Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-[#efe6dd] p-2 py-6 h-full flex flex-col gap-2">
        <CardHeader>
          <CardTitle className="text-[#9a0002]">Daily Attendance Log</CardTitle>

          <div className="grid grid-cols-2 gap-3">
            <Button onClick={handleTimeIn} className={`h-5 py-3 rounded-sm w-full text-[10px] cursor-pointer text-[#9a0002] bg-[#e5b85c] ${todayDtr?.time_in ? 'bg-[#4f9d69]' : ''}`} disabled={!!todayDtr?.time_in}>Time in</Button>
            <Button onClick={handleTimeOut} className="h-5 py-3  rounded-sm w-full text-[10px] cursor-pointer  text-[#9a0002] bg-[#e5b85c]">Time out</Button>
          </div>
        </CardHeader>

        <CardContent>
          <div className="flex flex-col h-full rounded-xl 
          border border-white/60 bg-[#efe6dd]/30 backdrop-blur-md 
          shadow-[inset_0_4px_12px_rgba(0,0,0,0.15),inset_0_2px_4px_rgba(0,0,0,0.1)] px-4 py-3 gap-2">
            <div className="w-full text-center text-[#9a0002] text-[14px]">
              {dateToday}
            </div>

            <div className="w-full text-center text-[#9a0002] text-[60px] font-bold">
              {currentTime}
            </div>


            <div className="flex flex-row justify-between">
              <div className="w-full text-[#9a0002] text-[12px] font-bold">Time in: {timeInDisplay}</div>
              <div className="w-full text-[#9a0002] text-[12px] font-bold">Time out: {timeOutDisplay}</div>
            </div>

          </div>
        </CardContent>

          <div className="px-4">
          <Button className="rounded-sm h-6 w-full text-[10px] text-[#efe6dd] bg-[#9a0002] cursor-pointer hover:bg-[#9a0002]/30" onClick={handleLogout}>
            Log Out
          </Button> 
            </div>  
      </Card>


      <div>
      </div>

    </main>
  );
}

export default Home;