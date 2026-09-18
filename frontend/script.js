const API_BASE="/api/v1";
const ACCESS_TOKEN_KEY="access_token";
const REFRESH_TOKEN_KEY="refresh_token";

const $=(id)=>document.getElementById(id);
const escapeHtml=(value)=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));

function getAccessToken(){return localStorage.getItem(ACCESS_TOKEN_KEY)}
function getRefreshToken(){return localStorage.getItem(REFRESH_TOKEN_KEY)}
function setTokens(access,refresh){localStorage.setItem(ACCESS_TOKEN_KEY,access);if(refresh)localStorage.setItem(REFRESH_TOKEN_KEY,refresh)}
function removeTokens(){localStorage.removeItem(ACCESS_TOKEN_KEY);localStorage.removeItem(REFRESH_TOKEN_KEY)}
function isAuthenticated(){return !!getAccessToken()}

async function readResponse(response){
  const type=response.headers.get("content-type")||"";
  const text=await response.text();
  if(!text)return null;
  if(type.includes("application/json")){try{return JSON.parse(text)}catch{}}
  try{return JSON.parse(text)}catch{return {detail:text}}
}
async function refreshAccessToken(){
  const token=getRefreshToken(); if(!token)return false;
  try{
    const response=await fetch(API_BASE+"/auth/refresh",{method:"GET",headers:{Authorization:"Bearer "+token}});
    const data=await readResponse(response);
    if(response.ok&&data?.access_token){setTokens(data.access_token,data.refresh_token||token);return true}
  }catch(e){console.error("refresh:",e)}
  return false;
}
async function apiRequest(endpoint,options={},retry=true){
  const headers=new Headers(options.headers||{});
  if(!(options.body instanceof FormData)&&!headers.has("Content-Type"))headers.set("Content-Type","application/json");
  const access=getAccessToken(); if(access)headers.set("Authorization","Bearer "+access);
  const response=await fetch(API_BASE+endpoint,{...options,headers});
  if(response.status===401&&retry&&await refreshAccessToken())return apiRequest(endpoint,options,false);
  const data=await readResponse(response);
  if(!response.ok){
    if(response.status===401){removeTokens();if(!location.pathname.endsWith("login.html")&&!location.pathname.endsWith("register.html"))location.href="login.html"}
    throw new Error(data?.detail||data?.message||("HTTP "+response.status));
  }
  return data;
}

async function login(username,password){
  const body=new URLSearchParams({username,password});
  const response=await fetch(API_BASE+"/auth/login",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body});
  const data=await readResponse(response);
  if(!response.ok)throw new Error(data?.detail||"Не удалось войти");
  if(!data?.access_token)throw new Error("Сервер не вернул access token");
  setTokens(data.access_token,data.refresh_token); return data;
}
async function register(surname,name,username,email,password){
  const data=await apiRequest("/auth/register",{method:"POST",body:JSON.stringify({surname,name,username,email,password})});
  if(data?.access_token)setTokens(data.access_token,data.refresh_token); return data;
}
function logout(){removeTokens();location.href="login.html"}

async function uploadFile(file){
  const form=new FormData();form.append("uploaded_file",file);
  return apiRequest("/files/upload",{method:"POST",body:form});
}
async function createProjectData(data){return apiRequest("/projects/create",{method:"POST",body:JSON.stringify(data)})}
async function getProjects(page=1,size=10){return apiRequest(`/projects/?page=${page}&size=${size}`)}
async function getMyProjects(page=1,size=10){return apiRequest(`/projects/about-me?page=${page}&size=${size}`)}
async function getProject(id){return apiRequest(`/projects/${id}`)}
async function getUserById(id){return apiRequest(`/users/${id}`)}
async function getUserProjects(id,page=1,size=10){return apiRequest(`/projects/user/${id}?page=${page}&size=${size}`)}
async function getCurrentUser(){return apiRequest("/users/about-me")}
async function updateProfile(data){return apiRequest("/users/about-me",{method:"PUT",body:JSON.stringify(data)})}
async function deleteAccountRequest(){return apiRequest("/users/about-me",{method:"DELETE"})}
async function updateProject(id,data){return apiRequest(`/projects/${id}`,{method:"PATCH",body:JSON.stringify(data)})}
async function deleteProject(id){return apiRequest(`/projects/${id}`,{method:"DELETE"})}
async function getTags(id){return apiRequest(`/tags/project/${id}`)}
async function createTag(name,project_id){return apiRequest("/tags/create",{method:"POST",body:JSON.stringify({name,project_id})})}
async function deleteTag(id){return apiRequest(`/tags/${id}`,{method:"DELETE"})}

function setupDropdown(){
  const btn=$("avatarBtn"),menu=$("dropdownMenu");if(!btn||!menu)return;
  btn.addEventListener("click",e=>{e.stopPropagation();menu.classList.toggle("show")});
  document.addEventListener("click",e=>{if(!menu.contains(e.target)&&e.target!==btn)menu.classList.remove("show")});
  $("logoutBtn")?.addEventListener("click",logout);
}

function statusLabel(status){return status==="completed"?"Готов":status==="rendering"?"Рендеринг":"Неизвестно"}
function projectCard(project){
  const id=encodeURIComponent(project.id);
  const name=escapeHtml(project.name||"Без названия");
  const desc=escapeHtml(project.description||"Без описания");
  const visibility=project.visibility==="private"?"Приватный":"Публичный";
  return `<article class="project-card" data-id="${id}">
    <div class="project-thumbnail"><div class="thumbnail-placeholder"><i class="fas fa-cube"></i><span>PRIZM</span></div>
      <span class="badge-${project.visibility==="private"?"private":"public"} badge"><i class="fas fa-${project.visibility==="private"?"lock":"globe"}"></i> ${visibility}</span>
      <span class="project-status-badge status-${project.status||""}">${statusLabel(project.status)}</span>
    </div><div class="project-info"><h3>${name}</h3><p class="project-description">${desc}</p></div>
  </article>`
}
function bindProjectCards(container){container.querySelectorAll(".project-card").forEach(card=>card.addEventListener("click",()=>location.href="project.html?id="+card.dataset.id))}

function renderPagination(current,hasNext,prev,next,info){
  if(prev){prev.disabled=current<=1;prev.onclick=()=>current>1&&loadProjects(current-1)}
  if(next){next.disabled=!hasNext;next.onclick=()=>hasNext&&loadProjects(current+1)}
  if(info)info.textContent="Страница "+current
}
let publicPage=1;
async function loadProjects(page=1){
  const grid=$("projectsGrid"),loading=$("loading");if(!grid)return;
  publicPage=page;loading&&(loading.style.display="block");
  try{
    const data=await getProjects(page,10),items=data?.project_list||[];
    grid.innerHTML=items.length?items.map(projectCard).join(""):`<div class="empty-state" style="grid-column:1/-1"><i class="fas fa-box-open"></i><p>Публичных проектов пока нет</p></div>`;
    bindProjectCards(grid);renderPagination(page,items.length===10,$("prevPage"),$("nextPage"),$("pageInfo"));
  }catch(e){grid.innerHTML=`<div class="error-message" style="grid-column:1/-1">Ошибка загрузки: ${escapeHtml(e.message)}</div>`}
  finally{if(loading)loading.style.display="none"}
}
let myPage=1;
async function loadMyProjects(page=1){
  const grid=$("myProjectsGrid"),loading=$("loading");if(!grid)return;
  myPage=page;loading&&(loading.style.display="block");
  try{
    const data=await getMyProjects(page,10),items=data?.project_list||[];
    grid.innerHTML=items.length?items.map(projectCard).join(""):`<div class="empty-state" style="grid-column:1/-1"><i class="fas fa-folder-open"></i><p>У вас пока нет проектов</p><a class="btn btn-primary" href="create.html">Создать проект</a></div>`;
    bindProjectCards(grid);renderPagination(page,items.length===10,$("prevPage"),$("nextPage"),$("pageInfo"));
  }catch(e){grid.innerHTML=`<div class="error-message" style="grid-column:1/-1">Ошибка загрузки: ${escapeHtml(e.message)}</div>`}
  finally{if(loading)loading.style.display="none"}
}

function hexRgb(hex){return[0,1,2].map(i=>parseFloat((parseInt(hex.slice(1+i*2,3+i*2),16)/255).toFixed(6)))}
function normalizeSun(x,y,z){const l=Math.hypot(x,y,z)||1;return[x/l,y/l,z/l]}
function initSunEditor(){
  const host=$("sunSphereContainer");if(!host||typeof THREE==="undefined")return;
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(42,host.clientWidth/host.clientHeight,.1,100);camera.position.set(0,0,4);
  const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(host.clientWidth,host.clientHeight);renderer.setClearColor(0x17191b);host.appendChild(renderer.domElement);
  const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=3;controls.maxDistance=7;
  const sphere=new THREE.Mesh(new THREE.SphereGeometry(1.25,48,32),new THREE.MeshBasicMaterial({color:0x35383d,wireframe:true,transparent:true,opacity:.72}));scene.add(sphere);
  const axes=new THREE.AxesHelper(1.55);scene.add(axes);
  const sun=new THREE.Mesh(new THREE.SphereGeometry(.085,20,12),new THREE.MeshBasicMaterial({color:0xffaa00}));scene.add(sun);
  const ring=new THREE.Mesh(new THREE.RingGeometry(.11,.13,32),new THREE.MeshBasicMaterial({color:0xffaa00,side:THREE.DoubleSide,transparent:true,opacity:.85}));ring.rotation.x=Math.PI/2;scene.add(ring);
  const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();let dragging=false;
  function setSun(v){const n=normalizeSun(v.x,v.y,v.z),p=new THREE.Vector3(...n).multiplyScalar(1.25);sun.position.copy(p);ring.position.copy(p);$("sunX").value=n[0].toFixed(2);$("sunY").value=n[1].toFixed(2);$("sunZ").value=n[2].toFixed(2)}
  function pick(e){const r=host.getBoundingClientRect();pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1;raycaster.setFromCamera(pointer,camera);const hit=raycaster.intersectObject(sphere)[0];if(hit)setSun(hit.point)}
  renderer.domElement.addEventListener("pointerdown",e=>{dragging=true;renderer.domElement.setPointerCapture(e.pointerId);pick(e)});
  renderer.domElement.addEventListener("pointermove",e=>{if(dragging)pick(e)});
  renderer.domElement.addEventListener("pointerup",()=>dragging=false);
  $("resetSun")?.addEventListener("click",()=>setSun({x:0,y:1,z:0}));
  function animate(){controls.update();renderer.render(scene,camera);requestAnimationFrame(animate)}animate();setSun({x:0,y:1,z:0});
  window.addEventListener("resize",()=>{const w=host.clientWidth,h=host.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)});
  return{getDirection:()=>normalizeSun(parseFloat($("sunX").value),parseFloat($("sunY").value),parseFloat($("sunZ").value)),setColor:c=>{sun.material.color.set(c);ring.material.color.set(c)}}
}

async function initCreate(){
  const form=$("createProjectForm");if(!form)return;
  const sunEditor=initSunEditor();
  const sunColor=$("sunColor"),bgColor=$("bgColor"),sunSize=$("sunSize"),sizeValue=$("sunSizeValue");
  function syncColors(){ $("sunColorPreview").style.background=sunColor.value;$("bgColorPreview").style.background=bgColor.value;sunEditor?.setColor(sunColor.value);sizeValue.textContent=Number(sunSize.value).toFixed(2)}
  sunColor.addEventListener("input",syncColors);bgColor.addEventListener("input",syncColors);sunSize.addEventListener("input",syncColors);syncColors();
  form.addEventListener("submit",async e=>{
    e.preventDefault();const error=$("createError"),success=$("createSuccess");error.style.display="none";success.style.display="none";
    const file=$("glbFile").files[0],name=$("projectName").value.trim(),description=$("projectDescription").value.trim();
    if(!file)return error.style.display="block",error.textContent="Выберите GLB-файл";
    if(file.size>20*1024*1024)return error.style.display="block",error.textContent="Файл слишком большой. Максимум 20 МБ";
    try{
      const fileData=await uploadFile(file);
      const direction=sunEditor?.getDirection()||[0,1,0];
      const projectData={project:{name,description,source_file_id:fileData.id,visibility:document.querySelector("input[name=visibility]:checked").value},render:{width:+$("width").value,height:+$("height").value,samples:+$("samples").value,denoiser:$("denoiser").value==="true",gpu:$("gpu").value==="true",background:hexRgb(bgColor.value),sun:{direction,color:hexRgb(sunColor.value),exponent:Math.round(+sunSize.value*600)}}};
      const result=await createProjectData(projectData);success.style.display="block";success.textContent="Проект создан. Рендер запущен.";setTimeout(()=>location.href="project.html?id="+result.id,700);
    }catch(e){error.style.display="block";error.textContent=e.message||"Не удалось создать проект"}
  })
}

async function loadProjectDetail(id){
  const container=$("projectDetail");if(!container)return;
  try{
    const project=await getProject(id),owner=await getUserById(project.user_id).catch(()=>null),me=await getCurrentUser().catch(()=>null),isOwner=me?.id===project.user_id;
    const render=project.render||{},renderUrl=render.url||null;
    container.innerHTML=`<article class="project-detail-content">
      <div class="project-detail-header"><div class="project-detail-header-top"><div><h1>${escapeHtml(project.name)}</h1><div class="project-detail-meta"><span class="badge">${project.visibility==="private"?"🔒 Приватный":"🌐 Публичный"}</span><span class="badge status-${project.status}">${statusLabel(project.status)}</span></div></div>
      ${isOwner?`<div class="project-actions"><button class="btn btn-secondary" id="editProjectBtn"><i class="fas fa-pen"></i> Редактировать</button><button class="btn btn-danger" id="deleteProjectBtn"><i class="fas fa-trash"></i> Удалить</button></div>`:""}</div></div>
      <div id="editProjectForm" style="display:none" class="edit-form"><form id="updateProjectForm"><div class="form-group"><label>Название</label><input id="editProjectName" value="${escapeHtml(project.name)}" maxlength="30" required></div><div class="form-group"><label>Описание</label><textarea id="editProjectDescription" maxlength="512">${escapeHtml(project.description)}</textarea></div><div class="form-group"><label>Доступ</label><select id="editProjectVisibility"><option value="public" ${project.visibility==="public"?"selected":""}>Публичный</option><option value="private" ${project.visibility==="private"?"selected":""}>Приватный</option></select></div><div class="form-actions"><button class="btn btn-primary" type="submit">Сохранить</button><button class="btn btn-secondary" type="button" id="cancelEditProject">Отмена</button></div></form><div id="updateProjectError" class="error-message" style="display:none"></div><div id="updateProjectSuccess" class="success-message" style="display:none"></div></div>
      <div class="project-detail-body"><div><section class="detail-section"><h3>Описание</h3><p>${escapeHtml(project.description||"Нет описания")}</p></section>
      <section class="detail-section"><h3>Файлы</h3><div class="file-item"><i class="fas fa-file"></i><span>Исходный GLB</span>${project.url?`<a class="btn btn-sm btn-secondary" href="${project.url}" target="_blank">Скачать</a>`:`<span class="file-missing">Недоступен</span>`}</div><div class="file-item"><i class="fas fa-image"></i><span>${escapeHtml(render.file?.name||"Результат рендера")}</span>${renderUrl?`<a class="btn btn-sm btn-primary" href="${renderUrl}" target="_blank">Открыть</a>`:`<span class="file-missing">${project.status==="rendering"?"Рендерится":"Не готов"}</span>`}</div></section>
      <section class="detail-section"><h3>Настройки рендера</h3><ul class="render-settings-list"><li><span>Разрешение</span><span>${render.width||"—"} × ${render.height||"—"}</span></li><li><span>Сэмплы</span><span>${render.samples||"—"}</span></li><li><span>Денойзер</span><span>${render.denoiser?"Включен":"Выключен"}</span></li><li><span>GPU</span><span>${render.gpu?"Включен":"Выключен"}</span></li></ul></section>
      <div class="owner-card" onclick="location.href='profile.html?id=${encodeURIComponent(project.user_id)}'"><div class="owner-avatar"><i class="fas fa-user-circle"></i></div><div><div class="owner-name">${escapeHtml(owner?.name?owner.name+" "+owner.surname:owner?.username||("Пользователь #"+project.user_id))}</div><div class="owner-username">${owner?.username?"@"+escapeHtml(owner.username):""}</div><div class="owner-hint">Открыть профиль</div></div></div></div>
      <aside><div class="tags-section"><div class="tags-header"><h3><i class="fas fa-tags"></i> Теги</h3>${isOwner?'<button id="showTagForm" class="btn btn-sm btn-secondary"><i class="fas fa-plus"></i></button>':""}</div>${isOwner?'<div id="addTagForm" style="display:none"><div class="add-tag-input-group"><input id="newTagInput" class="tag-input" maxlength="25" placeholder="Новый тег"><button id="addTagBtn" class="btn btn-sm btn-success">OK</button></div></div>':""}<div id="tagsList" class="tags-list">Загрузка...</div></div></aside></div>
      <section class="project-detail-render"><div class="render-preview-large"><h3>Результат рендера</h3>${renderUrl?'<img class="render-image-large" src="'+renderUrl+'" alt="Результат рендера">':'<div class="no-render-large"><i class="fas fa-image"></i><p>'+(project.status==="rendering"?"Рендер выполняется":"Результат пока не готов")+'</p><small>'+(project.status==="rendering"?"Обновите страницу позже":"Здесь появится PNG после завершения рендера")+'</small></div>'}</div></section>
    </article>`;
    if(isOwner){
      $("editProjectBtn").onclick=()=>{$("editProjectForm").style.display=$("editProjectForm").style.display==="none"?"block":"none"};
      $("cancelEditProject").onclick=()=>{$("editProjectForm").style.display="none"};
      $("updateProjectForm").onsubmit=async e=>{e.preventDefault();try{await updateProject(id,{name:$("editProjectName").value.trim(),description:$("editProjectDescription").value.trim(),visibility:$("editProjectVisibility").value});$("updateProjectSuccess").style.display="block";$("updateProjectSuccess").textContent="Сохранено";setTimeout(()=>loadProjectDetail(id),400)}catch(x){$("updateProjectError").style.display="block";$("updateProjectError").textContent=x.message}};
      $("deleteProjectBtn").onclick=()=>openProjectDelete(project);
    }
    await loadTags(id,isOwner);
  }catch(e){container.innerHTML=`<div class="error-message">Ошибка загрузки проекта: ${escapeHtml(e.message)}</div>`}
}
async function loadTags(id,isOwner){
  const box=$("tagsList");if(!box)return;
  try{const data=await getTags(id),tags=data?.tag_list||[];box.innerHTML=tags.length?tags.map(t=>`<span class="tag-chip">${escapeHtml(t.name)}${isOwner?`<button class="tag-delete" data-id="${t.id}" title="Удалить">×</button>`:""}</span>`).join(""):"<span style='color:#666;font-size:12px'>Нет тегов</span>";
  box.querySelectorAll(".tag-delete").forEach(b=>b.onclick=async e=>{e.stopPropagation();try{await deleteTag(b.dataset.id);loadTags(id,isOwner)}catch(x){alert(x.message)}})
  if(isOwner){$("showTagForm").onclick=()=>{$("addTagForm").style.display=$("addTagForm").style.display==="none"?"block":"none"};$("addTagBtn").onclick=async()=>{const n=$("newTagInput").value.trim();if(n.length<3||n.length>25)return alert("Тег должен содержать 3–25 символов");try{await createTag(n,id);$("newTagInput").value="";loadTags(id,isOwner)}catch(x){alert(x.message)}}}
  }catch(e){box.textContent="Не удалось загрузить теги"}
}
let profileState={userId:null,page:1};
async function loadProfile(userId=null,page=1){
  const box=$("profileContent");if(!box)return;
  try{
    const user=userId?await getUserById(userId):await getCurrentUser(),own=!userId,projects=own?await getMyProjects(page,10):await getUserProjects(user.id,page,10),items=projects?.project_list||[];
    box.innerHTML=`<section class="profile-card"><div class="profile-header"><div class="profile-avatar-large"><i class="fas fa-user-circle"></i></div><div class="profile-info"><h1>${escapeHtml(user.username)}</h1><p class="profile-name">${escapeHtml(user.name+" "+user.surname)}</p>${own?`<p class="profile-email">${escapeHtml(user.email)}</p>`:""}<p class="profile-date">Регистрация: ${new Date(user.registration_date).toLocaleDateString("ru-RU")}</p><div class="profile-stats">${items.length===10?"10+":items.length} проектов</div></div></div>${own?`<div class="profile-actions"><button id="editProfileBtn" class="btn btn-secondary">Редактировать</button><button id="deleteAccountBtn" class="btn btn-danger">Удалить аккаунт</button></div><div id="editForm" class="edit-form" style="display:none"><form id="profileForm"><div class="form-row"><div class="form-group"><label>Фамилия</label><input id="editSurname" value="${escapeHtml(user.surname)}" required></div><div class="form-group"><label>Имя</label><input id="editName" value="${escapeHtml(user.name)}" required></div></div><div class="form-group"><label>Username</label><input id="editUsername" value="${escapeHtml(user.username)}" required></div><div class="form-group"><label>Email</label><input id="editEmail" value="${escapeHtml(user.email)}" type="email" required></div><div class="form-actions"><button class="btn btn-primary">Сохранить</button><button type="button" id="cancelProfileEdit" class="btn btn-secondary">Отмена</button></div></form><div id="profileEditError" class="error-message" style="display:none"></div></div>`:""} </section><section class="profile-projects-section"><h2>Проекты</h2>${items.length?'<div class="projects-grid">'+items.map(projectCard).join("")+'</div>':'<div class="empty-state"><i class="fas fa-box-open"></i><p>Проектов нет</p></div>'}<div class="pagination"><button id="profilePrev" class="btn btn-secondary" disabled>Назад</button><span class="page-info">Страница ${page}</span><button id="profileNext" class="btn btn-secondary" ${items.length<10?"disabled":""}>Вперед</button></div></section>`;
    bindProjectCards(box);
    if(own){$("editProfileBtn").onclick=()=>{$("editForm").style.display=$("editForm").style.display==="none"?"block":"none"};$("cancelProfileEdit").onclick=()=>{$("editForm").style.display="none"};$("profileForm").onsubmit=async e=>{e.preventDefault();try{await updateProfile({surname:$("editSurname").value.trim(),name:$("editName").value.trim(),username:$("editUsername").value.trim(),email:$("editEmail").value.trim()});loadProfile(null,page)}catch(x){$("profileEditError").style.display="block";$("profileEditError").textContent=x.message}};$("deleteAccountBtn").onclick=()=>openAccountDelete(user)}
    $("profilePrev").disabled=page<=1;$("profilePrev").onclick=()=>page>1&&loadProfile(userId,page-1);$("profileNext").onclick=()=>items.length===10&&loadProfile(userId,page+1);
  }catch(e){box.innerHTML=`<div class="error-message">Ошибка загрузки профиля: ${escapeHtml(e.message)}</div>`}
}
function openAccountDelete(user){
  const modal=$("deleteAccountModal");modal.style.display="flex";$("modalUsernameDisplay").textContent="Введите: "+user.username;$("modalConfirmInput").value="";$("modalError").style.display="none";$("confirmDeleteAccount").disabled=true;
  $("modalConfirmInput").oninput=()=>{$("confirmDeleteAccount").disabled=$("modalConfirmInput").value!==user.username};
  $("confirmDeleteAccount").onclick=async()=>{try{await deleteAccountRequest();removeTokens();location.href="login.html"}catch(e){$("modalError").style.display="block";$("modalError").textContent=e.message}}
}
function openProjectDelete(project){
  const modal=$("deleteProjectModal");modal.style.display="flex";$("modalProjectNameDisplay").textContent="Введите: "+project.name;$("modalProjectConfirmInput").value="";$("modalProjectError").style.display="none";$("modalConfirmDeleteProject").disabled=true;
  $("modalProjectConfirmInput").oninput=()=>{$("modalConfirmDeleteProject").disabled=$("modalProjectConfirmInput").value!==project.name};
  $("modalConfirmDeleteProject").onclick=async()=>{try{await deleteProject(project.id);location.href="index.html"}catch(e){$("modalProjectError").style.display="block";$("modalProjectError").textContent=e.message}}
}
function setupModals(){
  [["closeDeleteAccount","deleteAccountModal"],["cancelDeleteAccount","deleteAccountModal"],["closeDeleteProject","deleteProjectModal"],["cancelDeleteProject","deleteProjectModal"]].forEach(([b,m])=>$(b)?.addEventListener("click",()=>$(m).style.display="none"));
  document.querySelectorAll(".modal-overlay").forEach(m=>m.addEventListener("click",e=>{if(e.target===m)m.style.display="none"}));
}
function setupAuth(){
  $("loginForm")?.addEventListener("submit",async e=>{e.preventDefault();const box=$("loginError");box.style.display="none";try{await login($("username").value.trim(),$("password").value);location.href="index.html"}catch(x){box.style.display="block";box.textContent=x.message}});
  $("registerForm")?.addEventListener("submit",async e=>{e.preventDefault();const box=$("registerError");box.style.display="none";if($("password").value!==$("confirmPassword").value){box.style.display="block";box.textContent="Пароли не совпадают";return}try{await register($("surname").value.trim(),$("name").value.trim(),$("username").value.trim(),$("email").value.trim(),$("password").value);location.href="index.html"}catch(x){box.style.display="block";box.textContent=x.message}});
}
document.addEventListener("DOMContentLoaded",()=>{
  const page=location.pathname.split("/").pop()||"index.html",publicPages=["login.html","register.html"];
  if(!isAuthenticated()&&!publicPages.includes(page)){location.href="login.html";return}
  if(isAuthenticated()&&publicPages.includes(page)){location.href="index.html";return}
  setupDropdown();setupAuth();setupModals();
  if(page==="index.html")loadProjects(1);
  if(page==="my-projects.html")loadMyProjects(1);
  if(page==="create.html")initCreate();
  if(page==="project.html"){const id=new URLSearchParams(location.search).get("id");id?loadProjectDetail(id):$("projectDetail").textContent="ID проекта не указан"}
  if(page==="profile.html"){const id=new URLSearchParams(location.search).get("id");loadProfile(id?Number(id):null,1)}
});
