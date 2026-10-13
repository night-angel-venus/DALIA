declare global {
    interface Window {
        pywebview? : {
            api: Record<string, (...args: any[]) => Promise<any>>;
        }
    }
}

export const bridge = {
    ready: () => typeof window.pywebview !== "undefined",

    async login(email: string, password: string) {
        return window.pywebview!.api.login(email, password);
    },

    async time_in(shiftType: String) {
        return window.pywebview!.api.time_int(shiftType);
    },

    async time_out() {
        return window.pywebview!.api.time_int();
    },

    async getStatus() {
        return window.pywebview!.api.get_status();
    },



}