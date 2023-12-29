# fastui-chat

Une interface utilisateur en python. 

## Comment l'utiliser ?

```bash
> ./dev-install.sh
```

Si cette commande ne fonctionne pas, faire :
```bash
> echo 'export PATH="$HOME/.rye/shims:$PATH"' >> ~/.bashrc
> source ~/.bashrc 
> rye sync
> rye shell
```

Puis,
```bash
> export OPENAI_API_KEY=valeur_de_la_cle_API
> python src/fastui_chat/app.py
```
