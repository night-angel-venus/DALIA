import {
    Field,
    FieldContent,
    FieldDescription,
    FieldError,
    FieldGroup,
    FieldLabel,
    FieldLegend,
    FieldSeparator,
    FieldSet,
    FieldTitle,
} from "../../components/ui/field"

import { Input } from "../../components/ui/input"

function LoginForm() {
    return (
        <FieldSet>
            <FieldLegend>Log in</FieldLegend>
            {/* <FieldDescription>This appears on invoices and emails.</FieldDescription> */}
            <FieldGroup>
                <Field>
                    <FieldLabel htmlFor="name">Email</FieldLabel>
                    <Input id="name" autoComplete="off" placeholder="Evil Rabbit" />
                    <FieldDescription>This appears on invoices and emails.</FieldDescription>
                </Field>
                <Field>
                    <FieldLabel htmlFor="username">Password</FieldLabel>
                    <Input id="username" autoComplete="off" aria-invalid />
                    <FieldError>Choose another username.</FieldError>
                </Field>
            </FieldGroup>
        </FieldSet>
    )
}

export default LoginForm