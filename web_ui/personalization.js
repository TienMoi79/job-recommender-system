/* Dữ liệu cá nhân thuộc trình duyệt hiện tại, không ghi vào catalog/GitHub.
 * Schema có phiên bản và danh sách trường cho phép để không lưu nhầm tệp nhị phân.
 * Module độc lập với DOM để kiểm thử cả khi bộ nhớ bị đầy hoặc bị chặn. */
(function (root) {
  'use strict';
  const PROFILE_KEY = 'jobvista-profile-v1';
  const SEARCH_KEY = 'jobvista-searches-v1';
  const text = (value, max) => typeof value === 'string' ? value.slice(0, max) : '';
  const years = value => value === '' || value === null ? '' :
    (typeof value === 'number' || typeof value === 'string') &&
    Number.isFinite(Number(value)) && Number(value) >= 0 && Number(value) <= 60 ? String(Number(value)) : null;
  const normalize = value => value.trim().replace(/\s+/g, ' ').toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd');

  class JobVistaStorage {
    constructor(storage) { this.storage = storage; this.failed = false; }
    read(key) {
      try { return JSON.parse(this.storage.getItem(key) || 'null'); }
      catch { this.failed = true; return null; }
    }
    write(key, value) {
      try { this.storage.setItem(key, JSON.stringify(value)); return true; }
      catch { this.failed = true; return false; }
    }
    removeProfile() {
      try { this.storage.removeItem(PROFILE_KEY); return true; }
      catch { this.failed = true; return false; }
    }
    static cleanProfile(value) {
      if (!value || value.version !== 1 || typeof value.text !== 'string' ||
          !value.text.trim() || value.text.length > 60000 || years(value.experience) === null) return null;
      const profile = value.profile || {};
      return { version: 1, text: value.text, filename: text(value.filename, 240), ocr: value.ocr === true,
        region: text(value.region, 50), experience: years(value.experience),
        experienceEdited: value.experienceEdited === true,
        updatedAt: Number.isFinite(value.updatedAt) ? value.updatedAt : 0,
        profile: { title: text(profile.title, 300),
          skills: Array.isArray(profile.skills) ? profile.skills.filter(s => typeof s === 'string').slice(0, 100).map(s => text(s, 100)) : [],
          locations: Array.isArray(profile.locations) ? profile.locations.filter(s => typeof s === 'string').slice(0, 20).map(s => text(s, 50)) : [],
          experience_years: years(profile.experience_years) === null || years(profile.experience_years) === '' ? null : Number(profile.experience_years),
          experience_status: text(profile.experience_status, 40) } };
    }
    readProfile() { return JobVistaStorage.cleanProfile(this.read(PROFILE_KEY)); }
    writeProfile(value) {
      const clean = JobVistaStorage.cleanProfile(value);
      return clean ? this.write(PROFILE_KEY, clean) : false;
    }
    static cleanSearch(value) {
      if (!value || typeof value !== 'object' || !['', '0', '1', '3'].includes(value.exp) ||
          !['all', 'dev', 'data', 'ai'].includes(value.category)) return null;
      const result = { id: text(value.id, 80), q: text(value.q, 200).trim(), region: text(value.region, 50),
        domain: text(value.domain, 150), exp: value.exp, category: value.category,
        updatedAt: Number.isFinite(value.updatedAt) ? value.updatedAt : 0 };
      return result.q || result.region || result.domain || result.exp || result.category !== 'all' ? result : null;
    }
    static searchKey(value) {
      return JSON.stringify([normalize(value.q), value.region, value.domain, value.exp, value.category]);
    }
    readSearches() {
      const data = this.read(SEARCH_KEY);
      if (data?.version !== 1 || !Array.isArray(data.items)) return [];
      const seen = new Set();
      return data.items.map(JobVistaStorage.cleanSearch).filter(item => {
        if (!item || !item.id || seen.has(JobVistaStorage.searchKey(item))) return false;
        seen.add(JobVistaStorage.searchKey(item)); return true;
      }).slice(0, 20);
    }
    writeSearches(items) {
      return this.write(SEARCH_KEY, { version: 1, items: items.map(JobVistaStorage.cleanSearch).filter(Boolean).slice(0, 20) });
    }
    static upsertSearch(items, value) {
      const item = JobVistaStorage.cleanSearch(value);
      if (!item) return items;
      const key = JobVistaStorage.searchKey(item);
      const previous = items.find(entry => JobVistaStorage.searchKey(entry) === key);
      item.id = previous?.id || Date.now().toString(36) + Math.random().toString(36).slice(2, 9);
      item.updatedAt = Date.now();
      return [item, ...items.filter(entry => JobVistaStorage.searchKey(entry) !== key)].slice(0, 20);
    }
  }
  root.JobVistaStorage = JobVistaStorage;
  if (typeof module !== 'undefined') module.exports = JobVistaStorage;
})(typeof globalThis !== 'undefined' ? globalThis : this);
