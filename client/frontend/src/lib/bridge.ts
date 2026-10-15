declare global {
    interface Window {
        pywebview? : {
            api: Record<string, (...args: any[]) => Promise<any>>;
        }
    }
}

export const bridge = {
    ready: () => typeof window.pywebview !== "undefined",

    async login(email: String, password: String) {
        return window.pywebview!.api.login(email, password);
    },

    async time_in(shiftType: String) {
        return window.pywebview!.api.time_in(shiftType);
    },

    async time_out() {
        return window.pywebview!.api.time_out();
    },

    async getStatus() {
        return window.pywebview!.api.get_status();
    },

    async getDtrToday() {
        return window.pywebview!.api.get_today();
    }



}