import React from 'react'
import { useState, useEffect } from 'react'
import { bridge } from '../lib/bridge';
import { Button } from '../components/ui/button';

import {
    Field,
    FieldGroup,
    FieldLabel,
    FieldSet,
} from "../components/ui/field"

import { Input } from "../components/ui/input"


function Login({ onSuccess }: { onSuccess: (user: any) => void }) {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    // const [error, setError] = useState("");
    const [ready, setReady] = useState(false);


    useEffect(() => {
        const check = setInterval(() => {
            if (bridge.ready()) {
                setReady(true);
                clearInterval(check);
            }
        }, 50);
        return () => clearInterval(check)
    }, []);


    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        // setError("")

        const result = await bridge.login(email, password);

        if (result.ok) {
            onSuccess(result.user);
        } else {
            // setError(result.error ?? "Login failed");
        }
    }


    return (
        <main className='p-14 w-screen h-screen border flex flex-col bg-[#9a0002]'>

            <div>
                <img src='../public/dalia_icon.svg' className='size-30 mx-auto mb-10 ' />
            </div>

            <form onSubmit={handleSubmit} className=''>
                <FieldSet>
                    <h1 className='text-[#efe6dd] font-bold text-[20px] w-full text-center mb-[10px]'>Log in</h1>
                    {/* <FieldDescription>This appears on invoices and emails.</FieldDescription> */}
                    <FieldGroup className='flex flex-col gap-4'>
                        <Field>
                            <FieldLabel htmlFor="name" className='text-[#efe6dd] font-bold'>Email</FieldLabel>
                            <Input id="name"
                                autoComplete="off"
                                type="email"
                                value={email}
                                placeholder='eann@bizsolvasia.com'
                                onChange={(e) => setEmail(e.target.value)}
                                className='rounded-sm bg-[#efe6dd] text-[14px]'
                            />
                            {/* <FieldDescription>This appears on invoices and emails.</FieldDescription> */}
                        </Field>
                        <Field>
                            <FieldLabel htmlFor="username" className='text-[#efe6dd] font-bold'>Password</FieldLabel>
                            <Input id="password"
                                autoComplete="off"
                                type="password"
                                value={password}
                                placeholder='Enter Password'
                                onChange={(e) => setPassword(e.target.value)}
                                className='rounded-sm bg-[#efe6dd] text-[14px]'
                            />
                            {/* <FieldError>Choose another username.</FieldError> */}
                        </Field>

                        <Button type="submit" className="rounded-sm bg-[#e5b85c] mt-6 text-[#9a0002] cursor-pointer">
                            {ready ? "Log in" : "Logging you in..."}
                        </Button>
                    </FieldGroup>
                </FieldSet>


            </form>


            {/* <LoginForm /> */}
        </main>
    )
}

export default Login