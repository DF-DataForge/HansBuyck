import { usePlugin } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Interaction } from "@web/public/interaction";
import { BootstrapInstance } from "@web/core/utils/bootstrap_plugin";

/**
 * Lightbox with previous/next for the "realisaties" galleries (.hb_gallery).
 * Reuses Odoo's own lightbox template so look & keyboard navigation are
 * identical to the standard image gallery snippet.
 * Interactions are not started in edit mode, so editing images stays possible.
 */
export class HbGalleryLightbox extends Interaction {
    static selector = ".hb_gallery";
    dynamicContent = {
        img: {
            "t-on-click": this.onClickImg,
        },
    };

    setup() {
        this.bootstrap = usePlugin(BootstrapInstance);
    }

    /**
     * @param {MouseEvent} ev
     */
    onClickImg(ev) {
        const imgEls = [...this.el.querySelectorAll("img")];
        const index = Math.max(0, imgEls.indexOf(ev.currentTarget));
        const images = imgEls.map((img) => {
            const clone = img.cloneNode(true);
            clone.removeAttribute("loading");
            return clone;
        });
        const modalEl = this.renderAt("website.image_mirror.lightbox", {
            images,
            index,
            shouldShowControls: images.length > 1,
            getIndicatorLabel: (itemPosition, total) =>
                _t("Slide %(itemPosition)s of %(total)s", { itemPosition, total }),
        })[0];
        this.insert(modalEl, document.body);
        const modal = this.bootstrap.getOrCreateInstance(Modal, modalEl, {
            keyboard: true,
            backdrop: true,
        });
        const disposeModal = () => {
            this.bootstrap.disposeBootstrapInstance(modal);
            modalEl.remove();
        };
        this.addListener(modalEl, "hidden.bs.modal", disposeModal, { once: true });
        this.registerCleanup(disposeModal);
        modal.show();
    }
}

registry
    .category("public.interactions")
    .add("website_hansbuyck.gallery_lightbox", HbGalleryLightbox);
