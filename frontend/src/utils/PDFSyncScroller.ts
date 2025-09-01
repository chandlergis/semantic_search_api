export class PDFSyncScroller {
  private container1: HTMLElement;
  private container2: HTMLElement;
  private isScrolling: boolean = false;
  private scrollHandler1: (event: Event) => void;
  private scrollHandler2: (event: Event) => void;
  private observer: MutationObserver | null = null;
  private retryCount: number = 0;
  private maxRetries: number = 10;

  constructor(container1: HTMLElement, container2: HTMLElement) {
    this.container1 = container1;
    this.container2 = container2;

    this.scrollHandler1 = () => {
      if (!this.isScrolling) {
        this.isScrolling = true;
        this.syncScroll(this.container1, this.container2);
        setTimeout(() => {
          this.isScrolling = false;
        }, 100);
      }
    };

    this.scrollHandler2 = () => {
      if (!this.isScrolling) {
        this.isScrolling = true;
        this.syncScroll(this.container2, this.container1);
        setTimeout(() => {
          this.isScrolling = false;
        }, 100);
      }
    };

    this.initSync();
  }

  private getScrollableElement(container: HTMLElement): HTMLElement | null {
    // 查找具有滚动条的PDF容器，优先级排序
    const selectors = [
      '.vue-pdf-embed > div', // 主滚动容器
      '.pdf-viewer', // 组件容器
      '.vue-pdf-embed', // PDF组件本身
      '.document-preview' // 外层容器
    ];

    console.log('正在查承PDF滚动容器...');
    
    for (const selector of selectors) {
      const element = container.querySelector(selector) as HTMLElement;
      if (element) {
        console.log(`找到元素: ${selector}`, {
          scrollHeight: element.scrollHeight,
          clientHeight: element.clientHeight,
          overflowY: window.getComputedStyle(element).overflowY,
          isScrollable: this.isScrollable(element)
        });
        
        if (this.isScrollable(element)) {
          console.log(`使用滚动容器: ${selector}`);
          return element;
        }
      }
    }

    // 如果没找到，使用容器本身
    if (this.isScrollable(container)) {
      console.log('使用容器本身作为滚动容器');
      return container;
    }

    console.warn('未找到合适的滚动容器');
    return null;
  }

  private isScrollable(element: HTMLElement): boolean {
    const style = window.getComputedStyle(element);
    const hasVerticalScrollbar = element.scrollHeight > element.clientHeight;
    const allowsScroll = style.overflowY === 'auto' || style.overflowY === 'scroll';
    
    // 放宽条件，只要有滚动内容就认为可滚动
    return hasVerticalScrollbar && (allowsScroll || style.overflow === 'auto' || style.overflow === 'scroll');
  }

  private initSync() {
    const setupScrollListeners = () => {
      const scrollEl1 = this.getScrollableElement(this.container1);
      const scrollEl2 = this.getScrollableElement(this.container2);

      if (scrollEl1 && scrollEl2) {
        console.log('PDF同步滚动初始化成功');
        scrollEl1.addEventListener('scroll', this.scrollHandler1, { passive: true });
        scrollEl2.addEventListener('scroll', this.scrollHandler2, { passive: true });
        
        // 存储实际的滚动元素引用
        this.container1 = scrollEl1;
        this.container2 = scrollEl2;
        
        if (this.observer) {
          this.observer.disconnect();
          this.observer = null;
        }
        
        return true;
      }
      return false;
    };

    // 立即尝试设置
    if (!setupScrollListeners()) {
      // 如果失败，使用MutationObserver监听DOM变化
      this.observer = new MutationObserver(() => {
        if (setupScrollListeners()) {
          return;
        }
        
        this.retryCount++;
        if (this.retryCount > this.maxRetries) {
          console.warn('PDF同步滚动初始化失败：超过最大重试次数');
          if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
          }
        }
      });

      this.observer.observe(document.body, {
        childList: true,
        subtree: true
      });

      // 使用定时器作为备用方案
      const retryTimer = setInterval(() => {
        if (setupScrollListeners()) {
          clearInterval(retryTimer);
        } else {
          this.retryCount++;
          if (this.retryCount > this.maxRetries) {
            clearInterval(retryTimer);
            console.warn('PDF同步滚动初始化失败：超过最大重试次数');
          }
        }
      }, 200);
    }
  }

  private syncScroll(source: HTMLElement, target: HTMLElement) {
    if (!source || !target) return;
    
    const sourceScrollTop = source.scrollTop;
    const sourceScrollHeight = source.scrollHeight;
    const sourceClientHeight = source.clientHeight;
    
    const targetScrollHeight = target.scrollHeight;
    const targetClientHeight = target.clientHeight;
    
    if (sourceScrollHeight <= sourceClientHeight || targetScrollHeight <= targetClientHeight) {
      return;
    }
    
    const scrollPercentage = sourceScrollTop / (sourceScrollHeight - sourceClientHeight);
    const targetScrollTop = scrollPercentage * (targetScrollHeight - targetClientHeight);
    
    target.scrollTo({
      top: targetScrollTop,
      behavior: 'auto'
    });
  }

  public destroy() {
    try {
      this.container1?.removeEventListener('scroll', this.scrollHandler1);
      this.container2?.removeEventListener('scroll', this.scrollHandler2);
      
      if (this.observer) {
        this.observer.disconnect();
        this.observer = null;
      }
      
      console.log('PDF同步滚动已销毁');
    } catch (error) {
      console.error('销毁PDF同步滚动时出错:', error);
    }
  }
}
