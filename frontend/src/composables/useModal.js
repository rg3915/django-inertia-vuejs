import { ref, watch, nextTick } from "vue"

/**
 * Composable para controlar modais com animação do PicoCSS.
 *
 * O PicoCSS espera que o modal use o HTMLDialogElement (showModal/close)
 * e que as classes modal-is-open, modal-is-opening e modal-is-closing
 * sejam aplicadas no <html> para controlar animações e scroll.
 */
export function useModal(dialogRef) {
    const isOpen = ref(false)
    const ANIMATION_DURATION = 400

    function open() {
        isOpen.value = true
        nextTick(() => {
            if (dialogRef.value) {
                dialogRef.value.showModal()
                document.documentElement.classList.add("modal-is-open", "modal-is-opening")
                setTimeout(() => {
                    document.documentElement.classList.remove("modal-is-opening")
                }, ANIMATION_DURATION)
            }
        })
    }

    function close() {
        document.documentElement.classList.add("modal-is-closing")
        setTimeout(() => {
            document.documentElement.classList.remove("modal-is-open", "modal-is-closing")
            if (dialogRef.value) {
                dialogRef.value.close()
            }
            isOpen.value = false
        }, ANIMATION_DURATION)
    }

    return { isOpen, open, close }
}
