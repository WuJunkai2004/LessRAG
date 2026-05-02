function debounce(func, wait) {
  let timeout;

  return function (...args) {
    const context = this;

    // 如果在等待期间再次触发，直接清除之前的计时器
    clearTimeout(timeout);

    // 重新开启计时
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}

export default debounce;
